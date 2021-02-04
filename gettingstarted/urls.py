from django.conf.urls import include, url
from django.urls import path

from django.contrib import admin

admin.autodiscover()

import linting.views

# Examples:
# url(r'^$', 'gettingstarted.views.home', name='home'),
# url(r'^blog/', include('blog.urls')),

urlpatterns = [
    url(r"^$", linting.views.index, name="index"),
    url(r"^validate", linting.views.validate, name="validate"),
]
