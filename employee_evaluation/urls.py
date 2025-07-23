from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name='employee_evaluation_main'),
    path('subordinates', views.get_subordinates, name='employee_evaluation_subordinates'),
    path('subordinates/filter', views.subordinates_apply_filters, name='employee_evaluation_subordinates_filter'),
    path('about', views.about, name='employee_evaluation_about'),
    path('about-block', views.about_block, name='employee_evaluation_about_block'),
    path('reviews', views.reviews, name='employee_evaluation_reviews'),
    path('review', views.review, name='employee_evaluation_review'),
    path('upload-review', views.upload_review, name='upload_review'),
    path('delete-review/<int:review_id>', views.delete_review, name='delete_review'),
]
