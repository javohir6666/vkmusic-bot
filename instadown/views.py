from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from .models import InstaLink
import requests, instaloader
from bs4 import BeautifulSoup

from django.conf import settings
import os
from django.contrib.auth.decorators import login_required
from datetime import datetime

def check_instagram_link(url):
    try:
        response = requests.get(url)
        if response.status_code == 200 and 'instagram.com' in url:
            return True
    except requests.exceptions.RequestException:
        return False
    return False

def download_instagram_video(url, link_id, username):
    loader = instaloader.Instaloader(download_videos=True, download_pictures=False, download_comments=False, download_geotags=False, save_metadata=False)
    shortcode = url.split('/')[-2]
    post = instaloader.Post.from_shortcode(loader.context, shortcode)
    
    # Creating a unique directory based on username and current time
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    target_folder = os.path.join(settings.MEDIA_ROOT, f'{username}/{current_time}')
    os.makedirs(target_folder, exist_ok=True)
    
    # Define the path where the video will be saved
    video_filename = os.path.join(target_folder, f'video_{link_id}.mp4')
    
    # Download the video
    video_url = post.video_url
    if video_url:
        response = requests.get(video_url)
        with open(video_filename, 'wb') as file:
            file.write(response.content)
    
    return video_url

@login_required
def index(request):
    if request.method == 'POST':
        url = request.POST.get('url')
        if url:
            is_valid = check_instagram_link(url)
            link, created = InstaLink.objects.get_or_create(url=url, user=request.user)
            link.is_valid = is_valid
            link.save()
            if is_valid:
                return redirect('download', link_id=link.id)
            else:
                return HttpResponse('Invalid Instagram URL')
    return render(request, 'index.html')

@login_required
def download(request, link_id):
    link = get_object_or_404(InstaLink, id=link_id)
    if link.is_valid:
        video_url = download_instagram_video(link.url, link.id, request.user.username)
        if video_url:
            return render(request, 'download.html', {'video_url': video_url})
    return HttpResponse('Invalid or no video found for the provided link.')


@login_required
def dashboard(request):
    links = InstaLink.objects.filter(user=request.user)
    return render(request, 'dashboard.html', {'links': links})