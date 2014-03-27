from django import forms
from django.forms.formsets import formset_factory
from django.contrib.auth import get_user_model
import models
from tinymce.widgets import TinyMCE

User =  get_user_model()

class CompetitionForm(forms.ModelForm):
    class Meta:
        model = models.Competition
        fields = ('title', 'description', 'image', 'has_registration', 'end_date', 'published')
        widgets = { 'description' : TinyMCE(attrs={'rows' : 20, 'class' : 'competition-editor-description'}, 
                                            mce_attrs={"theme" : "advanced", "cleanup_on_startup" : True, "theme_advanced_toolbar_location" : "top", "gecko_spellcheck" : True})}

class CompetitionPhaseForm(forms.ModelForm):
    class Meta:
        model = models.CompetitionPhase
        fields = ('phasenumber', 'label', 'start_date', 'max_submissions', 'scoring_program', 'reference_data', 'leaderboard_management_mode')
        widgets = { 'leaderboard_management_mode' : forms.Select(attrs={'class': 'competition-editor-phase-leaderboard-mode'}, choices=(('default', 'Default'), ('hide_results', 'Hide Results'))),
                    'DELETE' : forms.HiddenInput, 'phasenumber': forms.HiddenInput }
                
class PageForm(forms.ModelForm):
    class Meta:
        model = models.Page
        fields = ('category', 'rank', 'label', 'html', 'container')
        widgets = { 'html' : TinyMCE(attrs={'rows' : 20, 'class' : 'competition-editor-page-html'}, 
                                     mce_attrs={"theme" : "advanced", "cleanup_on_startup" : True, "theme_advanced_toolbar_location" : "top", "gecko_spellcheck" : True}),
                    'DELETE' : forms.HiddenInput, 'container' : forms.HiddenInput}

class CompetitionDatasetForm(forms.ModelForm):
    class Meta:
        model = models.Dataset

class CompetitionParticipantForm(forms.ModelForm):
    class Meta:
        model = models.CompetitionParticipant
