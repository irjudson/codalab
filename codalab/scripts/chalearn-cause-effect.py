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


#
#  Start ChaLearn Cause-Effect ----
#

# Create an owner
chalearn_ce_owner,_ = User.objects.get_or_create(email="ce@mail.com", username="chalearn-ce")
chalearn_ce_owner.set_password("abc123")
chalearn_ce_owner.save()

# ChaLearn Gesture Recognition
chalearn_ce_name = "Causality Challenge #3: Cause-Effect Pairs"
chalearn_ce_description = """
       The problem of attributing causes to effects is pervasive in science, medicine, economy and almost every aspects of our everyday life involving human reasoning and decision making.
        """
chalearn_ce,_ = Competition.objects.get_or_create(title=chalearn_ce_name, creator=chalearn_ce_owner, modified_by=chalearn_ce_owner,
                                                      defaults=dict(description=chalearn_ce_description))
details_category = ContentCategory.objects.get(name="Learn the Details")
participate_category = ContentCategory.objects.get(name="Participate")
pc,_ = PageContainer.objects.get_or_create(object_id=chalearn_ce.id, content_type=ContentType.objects.get_for_model(Competition))
chalearn_ce.save()

Page.objects.get_or_create(category=details_category, container=pc,  codename="overview",
                           defaults=dict(label="Overview", rank=0,
                                         html=open(os.path.join(os.path.dirname(__file__), "ce", "overview.html")).read()))
Page.objects.get_or_create(category=details_category, container=pc,  codename="evaluation", 
                           defaults=dict(label="Evaluation", rank=1,
                                         html=open(os.path.join(os.path.dirname(__file__), "ce", "evaluation.html")).read()))
Page.objects.get_or_create(category=details_category, container=pc,  codename="terms_and_conditions",
                    defaults=dict(rank=2, label="Terms and Conditions", html=open(os.path.join(os.path.dirname(__file__), "ce", "terms_and_conditions.html")).read()))

Page.objects.get_or_create(category=participate_category, container=pc,  codename="get_data",
                    defaults=dict(label="Get Data", rank=0, html=open(os.path.join(os.path.dirname(__file__), "ce", "data.html")).read()))
Page.objects.get_or_create(category=participate_category, container=pc,  codename="submit_results", html="", defaults=dict(label="Submit Results", rank=1))

# Logo
chalearn_ce.image = File(open(os.path.join(os.path.dirname(__file__), "ce", "logo.png"), 'rb'))

# Save the updates
chalearn_ce.save()

# Phases for the competition
day_delta = datetime.timedelta(days=30)
p1date = timezone.make_aware(datetime.datetime.combine(datetime.date(2012, 7, 6), datetime.time()), timezone.get_current_timezone())
p2date = timezone.make_aware(datetime.datetime.combine(datetime.date(2012, 10, 1), datetime.time()), timezone.get_current_timezone())
p1date = timezone.make_aware(datetime.datetime.combine(datetime.date(2013, 7, 15), datetime.time()), timezone.get_current_timezone())
p2date = timezone.make_aware(datetime.datetime.combine(datetime.date(2013, 8, 30), datetime.time()), timezone.get_current_timezone())
p, created = CompetitionPhase.objects.get_or_create(competition=chalearn_ce, phasenumber=1, label="Training Phase",
                                                                                                        start_date=p1date, max_submissions=100)
p, created = CompetitionPhase.objects.get_or_create(competition=chalearn_ce, phasenumber=2, label="Competition Phase",
                                                                                                        start_date=p2date, max_submissions=1)
#
#  End ChaLearn ----
#