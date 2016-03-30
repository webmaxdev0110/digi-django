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

from accounts.models import User


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        tag_lines = [
            ('Australia’s only digital platform <br/> to create, sign and send.',
             'The only place to create online forms for you and your clients to legally sign, witness, certify and complete. It’s simple, secure and efficient.',),
            ('Chasing your clients is painful,<br /> we fix this.',
             'Get your forms legally signed, witnessed, certified and completed online in minutes not weeks. We’re Australia’s only digital platform for end-to-end client onboarding.',),
            ('Capture <span class="solid-underline">new</span> leads and convert <span class="solid-underline">more</span> clients.',
             'Your abandoned online forms are now new leads that become your clients up to 45 times faster'
             ),
        ]
        tagline_index = random.randint(0, len(tag_lines) - 1)
        return {
            'tag_line': tag_lines[tagline_index],
            'tag_line_index': tagline_index
        }

    def post(self, request, *args, **kwargs):
        email = request.POST['email']

        user, _ = User.objects.get_or_create(
            username='pre_launch_' + uuid.uuid4().hex[:5],
            email=email,
            is_active=False,
            is_pre_launch_signup=True,
            country=''
        )
#
#         subject = "Beta user signed up"
#         body = """
# %s just signed up
# We have total %d beta users
# """ % (email, Person.query().count())
#
#         mail = EmailMultiAlternatives(
#             subject=subject,
#             body=body,
#             from_email="Robot <lilihan.it@gmail.com>",
#             to=["mccown@emondo.io", 'li@emondo.io'],
#             headers={"Reply-To": "mccown@emondo.io"}
#         )
#         mail.send()

        return HttpResponse('ok')
