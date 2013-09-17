#!/usr/bin/env python
# Run this with the python from the CodaLab virtual environment
# 

import sys, os.path, os, random, datetime
from django.utils import timezone
# This is a really, really long way around saying that if the script is in
#  codalab\scripts\users.py, we need to add, ../../../codalab to the sys.path to find the settings
root_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "codalab")
sys.path.append(root_dir)

# Set things for django configurations
os.environ.setdefault("DJANGO_CONFIGURATION", "Dev")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "codalab.settings")

# Import the configuration
from configurations import importer
importer.install()

from django.core.files import File
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

from apps.web.models import *

# Get the user model
User = get_user_model()

# Deal with time
start_date = timezone.now()

# Make the owner
email = "kalpathy@nmr.mgh.harvard.edu"
owner,cr = User.objects.get_or_create(username=email, email=email)
if cr:
  owner.set_password("C0daLab$jkc")
  owner.save()

# Make the competition
brats_name = "MICCAI Multimodal Brain Tumor Segmentation (BRaTS) Challenge"
brats_description = """
        The BRaTS challenge is designed to gauge the current state-of-the-art in automated brain tumor segmentation 
        and to compare between different methods. It is organized in conjuction with the MICCAI conference.
        """
brats2013,_ = Competition.objects.get_or_create(title=brats_name, creator=owner, modified_by=owner,defaults=dict(description=brats_description))
details_category = ContentCategory.objects.get(name="Learn the Details")
participate_category = ContentCategory.objects.get(name="Participate")
pc,_ = PageContainer.objects.get_or_create(object_id=brats2013.id, content_type=ContentType.objects.get_for_model(Competition))
brats2013.save()

Page.objects.get_or_create(category=details_category, container=pc,  codename="overview",
                           defaults=dict(label="Overview", rank=0,
                                         html=open(os.path.join(os.path.dirname(__file__), "brats2013/overview.html")).read()))
Page.objects.get_or_create(category=details_category, container=pc,  codename="evaluation", 
                           defaults=dict(label="Evaluation", rank=1,
                                         html=open(os.path.join(os.path.dirname(__file__), "brats2013/evaluation.html")).read()))
Page.objects.get_or_create(category=details_category, container=pc,  codename="terms_and_conditions",
                    defaults=dict(rank=2, label="Terms and Conditions", html=open(os.path.join(os.path.dirname(__file__), "brats2013/terms_and_conditions.html")).read()))

Page.objects.get_or_create(category=participate_category, container=pc,  codename="get_data",
                    defaults=dict(label="Get Data", rank=0, html=open(os.path.join(os.path.dirname(__file__), "brats2013/data.html")).read()))
Page.objects.get_or_create(category=participate_category, container=pc,  codename="submit_results", html="", defaults=dict(label="Submit Results", rank=1))

# Logo
brats2013.image = File(open(os.path.join(os.path.dirname(__file__), "brats2013", "logo.jpg"), 'rb'))

# Save the updates
brats2013.save()

# Phases for the competition
p1date = timezone.make_aware(datetime.datetime.combine(datetime.date(2013, 8, 30), datetime.time()), timezone.get_current_timezone())
p2date = timezone.make_aware(datetime.datetime.combine(datetime.date(2013, 9, 22), datetime.time()), timezone.get_current_timezone())
p, created = CompetitionPhase.objects.get_or_create(competition=brats2013, phasenumber=1, label="Training Phase",
                                                                                                        start_date=p1date, max_submissions=20)
p, created = CompetitionPhase.objects.get_or_create(competition=brats2013, phasenumber=2, label="Competition Phase",
                                                                                                        start_date=p2date, max_submissions=5)
for phase in CompetitionPhase.objects.filter(competition=brats2013):
    # note that we're using the same program and truth files for both phases 
    # but in reality they may be different.
    prog_file_path = os.path.join(root_dir, "media", "brats", "program.zip")
    if os.path.exists(prog_file_path):
        print "Setting program for phase: %s" % phase.label
        phase.scoring_program = File(open(prog_file_path, 'rb'))
        phase.save()
    else:
        print "No program file set for phase: %s" % phase.label
    reference_file_path = os.path.join(root_dir, "media", "brats", "testing-ref.zip")
    if os.path.exists(reference_file_path):
        print "Setting reference file for phase: %s" % phase.label
        phase.reference_data = File(open(reference_file_path, 'rb'))
        phase.save()
    else:
        print "No reference file set for phase: %s" % phase.label

brats_leaderboard_group_defs = {
    'patient'  : { 'label': 'Patient Data', 'order': 1},
	'synthetic': { 'label': 'Synthetic Data', 'order': 2} }

brats_leaderboard_defs = [
    #Patient data
    ('PatientDice', { 'label': 'Dice'}),
    ('PatientDiceComplete',  { 'group': 'patient', 'column_group':'PatientDice', 'label': 'Complete' }),
    ('PatientDiceCore',      { 'group': 'patient', 'column_group':'PatientDice', 'label': 'Core' }),
    ('PatientDiceEnhancing', { 'group': 'patient', 'column_group':'PatientDice', 'label': 'Enhancing' }),
    ('PatientSensitivity', { 'label': 'Sensitivity'}),
    ('PatientSensitivityComplete',  { 'group': 'patient', 'column_group':'PatientSensitivity', 'label': 'Complete' }),
    ('PatientSensitivityCore',      { 'group': 'patient', 'column_group':'PatientSensitivity', 'label': 'Core' }),
    ('PatientSensitivityEnhancing', { 'group': 'patient', 'column_group':'PatientSensitivity', 'label': 'Enhancing' }),
    ('PatientSpecificity', { 'label': 'Specificity'}),
    ('PatientSpecificityComplete',  { 'group': 'patient', 'column_group':'PatientSpecificity', 'label': 'Complete' }),
    ('PatientSpecificityCore',      { 'group': 'patient', 'column_group':'PatientSpecificity', 'label': 'Core' }),
    ('PatientSpecificityEnhancing', { 'group': 'patient', 'column_group':'PatientSpecificity', 'label': 'Enhancing' }),
    ('PatientHausdorff', { 'label': 'Hausdorff'}),
    ('PatientHausdorffComplete',  { 'group': 'patient', 'column_group':'PatientHausdorff', 'label': 'Complete', 'sort': 'asc' }),
    ('PatientHausdorffCore',      { 'group': 'patient', 'column_group':'PatientHausdorff', 'label': 'Core', 'sort': 'asc' }),
    ('PatientHausdorffEnhancing', { 'group': 'patient', 'column_group':'PatientHausdorff', 'label': 'Enhancing', 'sort': 'asc' }),
    ('PatientKappa', { 'group': 'patient', 'label': 'Kappa' }),
    ('PatientRank', { 'label': 'Rank'}),
    ('PatientRankComplete',  { 'group': 'patient', 'column_group':'PatientRank', 'label': 'Complete',
        'computed': {'operation': 'Avg', 'fields': ('PatientDiceComplete','PatientSensitivityComplete','PatientSpecificityComplete')} }),
    ('PatientRankCore',      { 'group': 'patient', 'column_group':'PatientRank', 'label': 'Core',
        'computed': {'operation': 'Avg', 'fields': ('PatientDiceCore','PatientSensitivityCore','PatientSpecificityCore')} }),
    ('PatientRankEnhancing', { 'group': 'patient', 'column_group':'PatientRank', 'label': 'Enhancing',
        'computed': {'operation': 'Avg', 'fields': ('PatientDiceEnhancing','PatientSensitivityEnhancing','PatientSpecificityEnhancing')} }),
    ('PatientRankOverall', { 'group': 'patient', 'label': 'Overall Rank', 'selection_default': 1,
        'computed': {'operation': 'Avg', 'fields': ('PatientDiceComplete','PatientSensitivityComplete','PatientSpecificityComplete',
                                                    'PatientDiceEnhancing','PatientSensitivityEnhancing','PatientSpecificityEnhancing',
                                                    'PatientDiceEnhancing','PatientSensitivityEnhancing','PatientSpecificityEnhancing')} }),
    #Synthetic data
    ('SyntheticDice', { 'label': 'Dice'}),
    ('SyntheticDiceComplete', { 'group': 'synthetic', 'column_group':'SyntheticDice', 'label': 'Complete' }),
    ('SyntheticDiceCore',     { 'group': 'synthetic', 'column_group':'SyntheticDice', 'label': 'Core' }),
    ('SyntheticSensitivity', { 'label': 'Sensitivity'}),
    ('SyntheticSensitivityComplete', { 'group': 'synthetic', 'column_group':'SyntheticSensitivity', 'label': 'Complete' }),
    ('SyntheticSensitivityCore',     { 'group': 'synthetic', 'column_group':'SyntheticSensitivity', 'label': 'Core' }),
    ('SyntheticSpecificity', { 'label': 'Specificity'}),
    ('SyntheticSpecificityComplete', { 'group': 'synthetic', 'column_group':'SyntheticSpecificity', 'label': 'Complete' }),
    ('SyntheticSpecificityCore',     { 'group': 'synthetic', 'column_group':'SyntheticSpecificity', 'label': 'Core' }),
    ('SyntheticHausdorff', { 'label': 'Hausdorff'}),
    ('SyntheticHausdorffComplete', { 'group': 'synthetic', 'column_group':'SyntheticHausdorff', 'label': 'Complete', 'sort': 'asc' }),
    ('SyntheticHausdorffCore',     { 'group': 'synthetic', 'column_group':'SyntheticHausdorff', 'label': 'Core', 'sort': 'asc' }),
    ('SyntheticKappa', { 'group': 'synthetic', 'label': 'Kappa' }),
    ('SyntheticRank', { 'label': 'Rank'}),
    ('SyntheticRankComplete', { 'group': 'synthetic', 'column_group':'SyntheticRank', 'label': 'Complete',
        'computed': {'operation': 'Avg', 'fields': ('SyntheticDiceComplete','SyntheticSensitivityComplete','SyntheticSpecificityComplete')} }),
    ('SyntheticRankCore',     { 'group': 'synthetic', 'column_group':'SyntheticRank', 'label': 'Core',
        'computed': {'operation': 'Avg', 'fields': ('SyntheticDiceCore','SyntheticSensitivityCore','SyntheticSpecificityCore')} }),
    ('SyntheticRankOverall',  { 'group': 'synthetic', 'label': 'Overall Rank', 'selection_default': 1,
        'computed': {'operation': 'Avg', 'fields': ('SyntheticDiceComplete','SyntheticSensitivityComplete','SyntheticSpecificityComplete',
                                                    'SyntheticDiceCore','SyntheticSensitivityCore','SyntheticSpecificityCore')} }) ]

brats_groups = {}
for (key,vals) in brats_leaderboard_group_defs.iteritems():
    rg,cr = SubmissionResultGroup.objects.get_or_create(
                competition=brats2013,
	            key=key, 
                defaults=dict(label=vals['label'], 
                ordering=vals['order']),)
    brats_groups[rg.key] = rg
    # All phases have the same leaderboard so add the group to each of them
    for gp in brats2013.phases.all():
        rgp,crx = SubmissionResultGroupPhase.objects.get_or_create(phase=gp, group=rg)

brats_column_groups = {}
brats_score_defs = {}
for key,vals in brats_leaderboard_defs:
    if 'group' not in vals:
        # Define a new grouping of scores
        s,cr = SubmissionScoreSet.objects.get_or_create(
                    competition=brats2013, 
                    key=key,
                    defaults=dict(label=vals['label']))
        brats_column_groups[key] = s
    else:
        # Create the score definition
        is_computed = 'computed' in vals
        sort_order = 'desc' if 'sort' not in vals else vals['sort']
        sdefaults = dict(label=vals['label'],numeric_format="2",show_rank=not is_computed,sorting=sort_order)
        if 'selection_default' in vals:
            sdefaults['selection_default'] = vals['selection_default']

        sd,cr = SubmissionScoreDef.objects.get_or_create(
                    competition=brats2013,
                    key=key,
                    computed=is_computed,
        		    defaults=sdefaults)
        if is_computed:
            sc,cr = SubmissionComputedScore.objects.get_or_create(scoredef=sd, operation=vals['computed']['operation'])
            for f in vals['computed']['fields']:
                # Note the lookup in brats_score_defs. The assumption is that computed properties are defined in 
                # brats_leaderboard_defs after the fields they reference.
                SubmissionComputedScoreField.objects.get_or_create(computed=sc, scoredef=brats_score_defs[f])
        brats_score_defs[sd.key] = sd

        # Associate the score definition with its column group
        if 'column_group' in vals:
            gparent = brats_column_groups[vals['column_group']]
            g,cr = SubmissionScoreSet.objects.get_or_create(
		            competition=brats2013,
                    parent=gparent,
		            key=sd.key,
		            defaults=dict(scoredef=sd, label=sd.label))
        else:
            g,cr = SubmissionScoreSet.objects.get_or_create(
		            competition=brats2013,
		            key=sd.key,
		            defaults=dict(scoredef=sd, label=sd.label))

        # Associate the score definition with its result group
        sdg,cr = SubmissionScoreDefGroup.objects.get_or_create(scoredef=sd,group=brats_groups[vals['group']])

# Add participants
status,cr = ParticipantStatus.objects.get_or_create(codename="approved")
participants = [("Keyvan Farahani", "farahank@mail.nih.gov", "C0daLab$kf"),
                ("Bjoern Menze", "bjoern@ethz.ch", "C0daLab$bm"),
                ("Mauricio Reyes", "mauricio.reyes@istb.unibe.ch", "C0daLab$mr"),
                ("Elizabeth Gerstner", "egerstner@partners.org", "C0daLab$eg"),
                ("Justin Kirby", "kirbyju@mail.nih.gov", "C0daLab$jk"),
                ("Jayashree Kalpathy-Cramer", "kalpathy@nmr.mgh.harvard.edu", "C0daLab$jkc"),
                ("Raphael Meier", "raphael.meier@istb.unibe.ch", "C0daLab$rm"),
                ("Nick Tustison", "ntustison@gmail.com", "C0daLab$nt"),
                ("Nicolas Cordier", "nicolas.cordier@inria.fr", "C0daLab$nc"),
                ("Syed Mohammad Shamim Reza", "sreza002@odu.edu", "C0daLab$smsr"),
                ("Joana Festa", "joana.araujo.festa@gmail.com", "C0daLab$jf"),
                ("Thomas J. Taylor", "thomas@infotechsoft.com", "C0daLab$tjt"),
                ("Patricia Buendia", "paty@infotechsoft.com", "C0daLab$pb"),
                ("Xiaotao Guo", "xg2145@columbia.edu", "C0daLab$xg"),
                ("Liang Zhao", "lzhao6@buffalo.edu", "C0daLab$lz"),
                ("Senan Doyle", "senan.doyle@gmail.com", "C0daLab$sd"),
                ("Hongzhi Wang", "hongzhiw@mail.med.upenn.edu", "C0daLab$hw"),
                ("Anant Madabhushi", "anantm@case.edu", "C0daLab$am"),
                ("Carlos Silva", "csilva@dei.uminho.pt", "C0daLab$cs"),
                ("Herve Delingette", "Herve.Delingette@inria.fr", "C0daLab$hd"),
                ("Nick Tustison", "NJT4N@virginia.edu", "C0daLab$nt"),
                ("Xiaotao Guo", "xg2145@columbia.edu", "C0daLab$xg"),
                ("Eric Chang", "eric.chang@microsoft.com", "C0daLab$ec"),
                ("Xiaojie Huang", "xiaojie.huang@yale.edu", "C0daLab$xh"),
                ("Raphael Meier", "raphael.meier@istb.unibe.ch", "C0daLab$rm"),
                ("Stefan Bauer", "stefan.bauer@istb.unibe.ch", "C0daLab$sb"),
                ("Liang Zhao", "lzhao6@buffalo.edu", "C0daLab$lz"),
                ("Sergio Pereira", "a55586@alunos.uminho.pt", "C0daLab$sp"),
                ("Duygu Sarikaya", "s_duygu@hotmail.com", "C0daLab$ds"),
                ("Simon Mercer", "simon.mercer@microsoft.com", "C0daLab$sm")]

for p_name, p_email, p_pass in participants:
  user,cr = User.objects.get_or_create(email=p_email, username=p_email)
  if cr:
    user.set_password(p_pass)
    user.save()

  print "Adding %s to competition %s with status %s" % (user, brats2013, status)
  resulting_participant, created = CompetitionParticipant.objects.get_or_create(user=user, competition=brats2013, status=status)
