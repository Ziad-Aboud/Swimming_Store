from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve
import os
from django.conf import settings

# Calculate the path to the Frontend folder (one directory up from BASE_DIR)
FRONTEND_DIR = os.path.join(settings.BASE_DIR.parent, 'Frontend', 'swim-store', 'swim-store')

# Customize the "View Mode" link in the admin
admin.site.site_header = "Django administration"
# Link to the relative route we are serving below
admin.site.site_url = "/store/index.html"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    
    # Serve the frontend files so the browser doesn't block them
    re_path(r'^store/(?P<path>.*)$', serve, {'document_root': FRONTEND_DIR}),
]