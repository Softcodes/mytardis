# Create your views here.
from django.template import Context, loader
from django.http import HttpResponse

from django.conf import settings

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User, Group
from django.http import HttpResponseRedirect, HttpResponseForbidden, \
    HttpResponseNotFound, HttpResponseServerError
from django.contrib.auth.decorators import login_required


from tardis.tardis_portal.ProcessExperiment import ProcessExperiment
from tardis.tardis_portal.forms import *
from tardis.tardis_portal.errors import *
from tardis.tardis_portal.logger import logger
from tardis.apps.mrtardis import *
from tardis.tardis_portal.models import Experiment

from tardis.apps.mrtardis.models import Job
from tardis.apps.mrtardis.models import MrTUser
import tardis.apps.mrtardis.backend.job

from tardis.apps.mrtardis.forms import *
import tardis.apps.mrtardis.utils as utils

def index(request, experiment_id):
    """return overview page for MR processing"""
    hpc_connection_test = utils.test_hpc_connection(request.user)
    c = Context({
            'experiment_id': experiment_id,
            'untested': not hpc_connection_test,
            })
    return render_to_response('mrtardis/index.html', c)

def startMR( request, experiment_id ):
    c = Context({
            'experiment_id': experiment_id,
            'upload_complete_url': '/apps/mrtardis/upload_complete/' + experiment_id + "/",
            })
    return render_to_response( 'mrtardis/startmr.html', c )

def jobstatus(request, experiment_id):
    if not request.user.is_authenticated():
        return "Not logged in"
    try:
        utils.update_job_status(experiment_id=experiment_id, user_id=request.user.id)
        jobs = Job.objects.filter(experiment_id=experiment_id)        

        c = Context({
                'jobs': jobs,
            })
    except Experiment.DoesNotExist, de:
        return return_response_not_found(request)

    return render_to_response('mrtardis/jobstatus.html', c)

def test_user_setup(request):
    if request.method == 'POST':
        form = HPCSetupForm(request.POST)
        if form.is_valid():
            hpc_username = form.cleaned_data['hpc_username']
            newHPCUser = MrTUser(user=request.user,
                                 hpc_username = hpc_username)
            newHPCUser.save()
            return HttpResponseRedirect('/apps/mrtardis/test_user_setup')
    else:
        user = MrTUser.objects.filter(user=request.user)
        if len(user) == 0 or user[0].hpc_username == "":
            setup = False
            form = HPCSetupForm()
            user = None
        else:
            form = None
            user = user[0]
            setup = True
    c = Context({
            'authenticated': request.user.is_authenticated(),
            'user': user,
            'setup': setup,
            'form': form,
            })
    return render_to_response("mrtardis/usersetup.html", c)


def upload_complete(request, experiment_id):
    cont = {
        'numberOfFiles': request.POST['filesUploaded'],
        'bytes': request.POST['allBytesLoaded'],
        'speed': request.POST['speed'],
        'errorCount': request.POST['errorCount'],
        }
    c = Context( cont )
    return render_to_response("mrtardis/upload_complete.html", c)

