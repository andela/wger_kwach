# -*- coding: utf-8 -*-

# This file is part of wger Workout Manager.
#
# wger Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# wger Workout Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License


import logging
import datetime
import json
import csv

from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _

from wger.manager.models import Workout
from wger.manager.helpers import render_workout_day
from wger.utils.helpers import check_token

from wger import get_version

logger = logging.getLogger(__name__)


def export_json(request, id, uidb64=None, token=None):
    # Load the workout
    if uidb64 is not None and token is not None:
        if check_token(uidb64, token):
            workout = get_object_or_404(Workout, pk=id)
        else:
            return HttpResponseForbidden()
    else:
        if request.user.is_anonymous():
            return HttpResponseForbidden()
    workout = get_object_or_404(Workout, pk=id, user=request.user)

    # Load the workout
    json_data, a_list = {}, []

    # Create the HttpResponse object with the appropriate json headers.

    json_data['comment'] = workout.comment
    json_data['creation_date'] = str(workout.creation_date)
    json_data['muscles'] = workout.canonical_representation['muscles']
    json_data['day_list'] = []

    for day in workout.canonical_representation['day_list']:

        for key, value in day.items():
            if key == 'obj':
                day['obj'] = str(day['obj']).strip('Day:')

            if key == 'days_of_week':
                value['day_list'] = [str(a_day).strip('DaysOfWeek:') for a_day in value['day_list']]

            if key == 'set_list':
                for a_set in value:
                    a_set['obj'] = a_set['obj'].id

                    for exe in a_set['exercise_list']:
                        exe['obj'] = str(exe['obj'])
                        exe['setting_obj_list'] = [str(obj_list).strip(
                            'Setting:') for obj_list in exe['setting_obj_list']]

                        exe['repetition_units'] = [str(reps) for reps in exe['repetition_units']]
                        exe['weight_units'] = [str(unit) for unit in exe['weight_units']]
                        exe['weight_list'] = [str(weight) for weight in exe['weight_list']]

        json_data['day_list'].append(day)

    # Create the HttpResponse object with the appropriate JSON headers.
    response = HttpResponse(json.dumps(json_data), content_type="application/json")
    response['Content-Disposition'] = 'attachment; filename=Workout-{0}.json'.format(id)
    return response


def export_csv(request, id, uidb64=None, token=None):

    # Load the workout
    if uidb64 is not None and token is not None:
        if check_token(uidb64, token):
            workout = get_object_or_404(Workout, pk=id)
        else:
            return HttpResponseForbidden()
    else:
        if request.user.is_anonymous():
            return HttpResponseForbidden()
    workout = get_object_or_404(Workout, pk=id, user=request.user)

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=Workout-{0}.csv'.format(id)

    writer = csv.writer(response)
    writer.writerow(['Id', 'Name', 'creation_date'])
    writer.writerow([workout.id, workout.comment, workout.creation_date])

    return response