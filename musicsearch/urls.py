from django.conf.urls import url
from .views import *

urlpatterns=[
    url("^$", index),
    url("^index.html$",index),
    url("^results.html$",show_results),
    url("^single.html$", show_details),
    url("^download$", download_mp3),
    url("^error.html$",error_proc),
]