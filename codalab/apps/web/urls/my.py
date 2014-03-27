from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from apps.web import views

partials_patterns = patterns(
    '',
    url(r'^_competitions_managed$',
        login_required(views.MyCompetitionsManagedPartial.as_view()),
        name='my_competitions_managed'),
    url(r'^_competitions_entered$',
        login_required(views.MyCompetitionsEnteredPartial.as_view()),
        name='my_competitions_entered'),
    url(r'^(?P<phase_id>\d+)/(?P<participant_id>\d+)/_submission_results',
        login_required(views.MySubmissionResultsPartial.as_view()),
        name='my_competition_submissions'),
)

urlpatterns = patterns(
    '',
    url(r'^$', views.my_index, name='competitions'),
    url(r'^competition/(?P<competition_id>\d+)/participants/',
        views.MyCompetitionParticipantView.as_view(),
        name='my_competition_participants'),
    url(r'^competition/(?P<competition_id>\d+)/submissions/',
        views.MyCompetitionSubmissionsPage.as_view(),
        name='my_competition_submissions'),
    url(r'^competition/submission/(?P<submission_id>\d+)/(?P<filetype>stdout.txt|stderr.txt|input.zip|prediction-output.zip|output.zip)$',
        views.MyCompetitionSubmisisonOutput.as_view(),
        name='my_competition_output'),
    url(r'^_partials/', include(partials_patterns)),
)
