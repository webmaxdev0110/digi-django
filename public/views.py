# -*- coding: utf-8 -*-

# Copyright 2015 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from django.http import HttpResponse
from django.views.generic import TemplateView
import random
import uuid
import os
from slacker import Slacker


from accounts.models import User


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        tag_lines = [
            ('Create simple, human-like, conversational forms  that autofill your existing documents',
             'emondo is the world\'s most secure platform for your clients to sign like Steve Jobs, '
            'witness, complete, and certify documents online. '
             'Instantly identify your clients in over 30 countries and stamp on the '
             'Blockchain. Get your free account today!',),
        ]
        tagline_index = random.randint(0, len(tag_lines) - 1)
        return {
            'tag_line': tag_lines[tagline_index],
            'tag_line_index': tagline_index
        }

    def post(self, request, *args, **kwargs):
        email = request.POST.get('email')

        user, _ = User.objects.get_or_create(
            username='pre_launch_' + uuid.uuid4().hex[:5],
            email=email,
            is_active=False,
            is_pre_launch_signup=True,
            signup_tag_index=request.POST.get('tagIndex'),
            signup_form_source=request.POST.get('formName'),
            country=''
        )
        # slack = Slacker(os.environ['SLACK_TOKEN'])
        # slack.chat.post_message('landingpagesubs', '%s signed up for beta launch' % email, 'Notification')
        return HttpResponse('ok')


class PublicPricingView(TemplateView):
    template_name = 'public/pricing.html'