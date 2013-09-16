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
day_delta = datetime.timedelta(days=30)
p1date = timezone.make_aware(datetime.datetime.combine(datetime.date(2012, 7, 6), datetime.time()), timezone.get_current_timezone())
p2date = timezone.make_aware(datetime.datetime.combine(datetime.date(2012, 10, 1), datetime.time()), timezone.get_current_timezone())
p1date = timezone.make_aware(datetime.datetime.combine(datetime.date(2013, 7, 15), datetime.time()), timezone.get_current_timezone())
p2date = timezone.make_aware(datetime.datetime.combine(datetime.date(2013, 8, 30), datetime.time()), timezone.get_current_timezone())
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

## Score Definitions
groups = {}

gorder = 1
for g in ({'key': 'patient', 'label': 'Patient Data'},
    {'key': 'synthetic', 'label': 'Synthetic Data'},
    ):
  rg,cr = SubmissionResultGroup.objects.get_or_create(competition=brats2013,
                  key=g['key'],
                  defaults=dict(label=g['label'],
                    ordering=gorder),
                  )
  gorder=gorder+1
  for gp in brats2013.phases.all():
    rgp,crx = SubmissionResultGroupPhase.objects.get_or_create(phase=gp, group=rg)
  groups[rg.key] = rg

for sdg in ( 
        ('synthetic',({'Dice': {'subs': (('SyntheticDiceComplete','Complete'),('SyntheticDiceCore','Core'))  } },
                      {'Sensitivity': {'subs': (('SyntheticSensitivityComplete','Complete'),('SyntheticSensitivityCore','Core'))  }},
                      {'Specificity': {'subs': (('SyntheticSpecificityComplete','Complete'),('SyntheticSpecificityCore','Core')) }},
                      {'Hausdorff': {'subs': (('SyntheticHausdorffComplete','Complete'),('SyntheticHausdorffCore','Core'))}},
                      {'Kappa': {'def':  ('SyntheticKappa','Kappa')}},
                      {'Rank': { 'computed': {'operation': 'Avg', 'key': 'synthetic_dice_rank', 'label': 'Rank', 'fields': ('SyntheticDiceComplete','SyntheticDiceCore')}}}) 
         ) ,

        ('patient',({'Dice': {'subs': (('PatientDiceComplete','Complete'),('PatientDiceCore','Core'),('PatientDiceEnhancing','Enhancing'))  } },
                    {'Sensitivity': {'subs': (('PatientSensitivityComplete','Complete'),('PatientSensitivityCore','Core'),('PatientSensitivityEnhancing','Enhancing'))  }},
                    {'Specificity': {'subs': (('PatientSpecificiyComplete','Complete'),('PatientSpecificiyCore','Core'),('PatientSpecificiyEnhancing','Enhancing')) }},
                    {'Hausdorff': {'subs': (('PatientHausdorffComplete','Complete'),('PatientHausdorffCore','Core'),('PatientHausdorffEnhancing','Enhancing'))}},
                    {'Kappa': {'def':  ('PatientKappa','Kappa')}},
                    {'Rank': { 'computed': {'operation': 'Avg', 'key': 'patient_dice_rank', 'label': 'Rank', 'fields': ('PatientDiceComplete','PatientDiceCore','PatientDiceEnhancing')}}})  ),
           ):
        

        rgroup,sg = sdg
        print "RGROUP", rgroup
        comp = []
        fields = {}
        for s in sg: 
                for label,e in s.items():
                        print "E",e
                        
                        for t,defs in e.items():
                                print "DEFS",defs
                                
                                if t == 'computed':
                                        g,cr = SubmissionScoreSet.objects.get_or_create(key=defs['key'],
                      competition=brats2013,
                      defaults=dict(label=label))
                                        comp.append((label,defs,g))
                                        print "COMPUTED"
                                elif t == 'subs':
                                        g,cr = SubmissionScoreSet.objects.get_or_create(key="%s%s" % (rgroup,label),
                      competition=brats2013,
                      defaults=dict(label=label))
                                        for sub in defs:
                                                print "SUB",sub
                                                

                                                sd,cr = SubmissionScoreDef.objects.get_or_create(competition=brats2013,key=sub[0],
                         defaults=dict(label=sub[1]))
                                                sdg0,cr = SubmissionScoreDefGroup.objects.get_or_create(scoredef=sd,group=groups[rgroup])
                                                fields[sd.key] = sd

                                                print " CREATED DEF", sd.key, sd.label
                                                #for p in brats2013.phases.all():
                                                #        sp,cr = SubmissionScorePhase.objects.get_or_create(scoredef=sd,phase=p)
                                                #        print "   ADDED TO PHASE"

                                                g2,cr = SubmissionScoreSet.objects.get_or_create(parent=g,
                         key=sub[0],
                         competition=brats2013,
                         defaults=dict(scoredef=sd,label=sub[1]))
                                                print " SUB GROUP", g2.label,g2.scoredef.key,g2.scoredef.label

                                elif t == 'def':
                                        g,cr = SubmissionScoreSet.objects.get_or_create(key="%s%s" % (rgroup,label),
                                                                                          competition=brats2013, defaults=dict(label=defs[1]))
                                        sd,cr = SubmissionScoreDef.objects.get_or_create(competition=brats2013,
                                                                                         key=defs[0],
                                                                                         defaults = dict(label=defs[1]))
                                        sdg0,cr = SubmissionScoreDefGroup.objects.get_or_create(scoredef=sd,group=groups[rgroup])
                                        fields[sd.key] = sd

                                        #for p in brats2013.phases.all():
                                        #        sp,cr = SubmissionScorePhase.objects.get_or_create(scoredef=sd,phase=p)
                                        g.scoredef = sd
                                        g.save()
        for label,defs,g in comp:
                sd,cr = SubmissionScoreDef.objects.get_or_create(competition=brats2013,
                                                                 key=defs['key'],
                                                                 defaults=dict(label=defs['label']),
                                                                 computed=True)
                sdg0,cr = SubmissionScoreDefGroup.objects.get_or_create(scoredef=sd,group=groups[rgroup])

                #for p in brats2013.phases.all():
                #        SubmissionScorePhase.objects.get_or_create(scoredef=sd,phase=p)
                sc,cr = SubmissionComputedScore.objects.get_or_create(scoredef = sd,
                                                                      operation = defs['operation'])
                for f in defs['fields']:
                        SubmissionComputedScoreField.objects.get_or_create(computed=sc,
                                                                           scoredef=fields[f])
                g.scoredef = sd
                g.save()

# Add participants
status,cr = ParticipantStatus.objects.get_or_create(codename="approved")
participants = [("Keyvan Farahani", "farahank@mail.nih.gov", "C0daLab$kf"),
                ("Bjoern Menze", "bjoern@ethz.ch", "C0daLab$bm"),
                ("Mauricio Reyes", "mauricio.reyes@istb.unibe.ch", "C0daLab$mr"),
                ("Elizabeth Gerstner", "NA", "C0daLab$eg"),
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
                ("Senan Doyle", "senan.doyle@gmail.com", "C0daLab$sd")]

for p_name, p_email, p_pass in participants:
  user,cr = User.objects.get_or_create(email=p_email, username=p_email)
  if cr:
    user.set_password(p_pass)
    user.save()

  print "Adding %s to competition %s with status %s" % (user, brats2013, status)
  resulting_participant, created = CompetitionParticipant.objects.get_or_create(user=user, competition=brats2013, status=status)
