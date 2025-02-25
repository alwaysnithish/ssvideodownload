from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, FileResponse
import yt_dlp
import os

DOWNLOADS_DIR = "Downloads/"
os.makedirs(DOWNLOADS_DIR, exist_ok=True)  # Ensure the folder exists

def home(request):
    context = {}

    if request.method == "POST":
        if "fetch_info" in request.POST:  # Fetch video details
            video_url = request.POST.get("url")

            if not video_url:
                context["error"] = "URL is required"
            else:
                try:
                    ydl_opts = {"format": "best"}
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(video_url, download=False)

                    context["title"] = info.get("title")
                    context["thumbnail"] = info.get("thumbnail")
                    context["video_url"] = video_url  # Pass for download

                except Exception as e:
                    context["error"] = f"Error: {str(e)}"

        elif "download_video" in request.POST:  # Start actual download
            video_url = request.POST.get("video_url")

            if not video_url:
                return HttpResponseBadRequest("No video URL provided")

            ydl_opts = {
                "format": "best",
                "outtmpl": DOWNLOADS_DIR + "%(title)s.%(ext)s",
            }

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(video_url, download=True)
                    file_path = ydl.prepare_filename(info)

                # Serve the file as an HTTP response
                response = FileResponse(open(file_path, "rb"), as_attachment=True, filename=os.path.basename(file_path))
                
                # Optionally, delete the file after sending (uncomment if needed)
                # os.remove(file_path)

                return response

            except Exception as e:
                return HttpResponseBadRequest(f"Download failed: {str(e)}")

    return render(request, "download.html", context)