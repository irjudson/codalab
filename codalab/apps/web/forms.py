from django import forms
from django.forms.formsets import formset_factory
from django.contrib.auth import get_user_model
import models

User =  get_user_model()

class CompetitionForm(forms.ModelForm):
    class Meta:
        model = models.Competition
        fields = ('title', 'description', 'image', 'has_registration', 'end_date', 'published')
        widgets = { 'description' : forms.Textarea(attrs={'rows' : 20, 'class' : 'competition-editor-description'}) }

class CompetitionPhaseForm(forms.ModelForm):
    class Meta:
        model = models.CompetitionPhase
        fields = ('label', 'start_date', 'max_submissions', 'scoring_program', 'reference_data', 'leaderboard_management_mode')
        widgets = { 'leaderboard_management_mode' : forms.Select(attrs={'class': 'competition-editor-phase-leaderboard-mode'}, choices=(('default', 'Default'), ('hide_results', 'Hide Results'))) }
                
class PageForm(forms.ModelForm):
    class Meta:
        model = models.Page
        fields = ('html',)
        widgets = { 'html' : forms.Textarea(attrs={'rows' : 20, 'class' : 'competition-editor-page-html' }) }

class CompetitionDatasetForm(forms.ModelForm):
    class Meta:
        model = models.Dataset

class CompetitionParticipantForm(forms.ModelForm):
    class Meta:
        model = models.CompetitionParticipant
