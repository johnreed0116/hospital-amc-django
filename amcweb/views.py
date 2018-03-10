from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

from mongoengine import errors as mngoengerrs
from pymongo import errors

from .forms import AppointmentForm, SubscribeEmail
from .models import Appointment, Patient, Prescription, Subscriber
from .utils.mailer import mail


def index(request):
    if request.method == 'POST':
        subscriber = Subscriber(request.POST['email'], request.POST['name'])
        try:
            new_sub = subscriber.save()
        except errors.AutoReconnect:
            context = {
                'err': 'DB_CONN_ERR',
                'msg': "Oops! There was an error. Please try after some time."
            }
            return render(request, 'amcweb/index.html', context)
        except mngoengerrs.ValidationError as err:
            print(err)
            context = {
                'err': 'BAD_INPUT',
                'msg': "There were errors in the info you entered. Enter valid info.",
                'form': request.POST
            }
            return render(request, 'amcweb/index.html', context)

        context = {'msg': "You've been subscribed to the newsletter. 🙂"}
        mail('new_subscriber', {'name': new_sub.name, 'email': new_sub.email})
        return render(request, 'amcweb/index.html', context)

    return render(request, 'amcweb/index.html', {})


class About(TemplateView):
    template_name = 'amcweb/about.html'


class Index(TemplateView):
    template_name = 'amcweb/index.html'


class MakeAppointment(FormView):
    template_name = 'amcweb/appointment.html'
    form_class = AppointmentForm

    def form_valid(self, form):
        form.create_appointment(form.cleaned_data)
        mail('new_appointment', { 'name': form.cleaned_data['name'], 'email': form.cleaned_data['email']})
        return render(self.request, 'amcweb/appointment.html', {'msg': {'msg': 'ye le', 'only': True, 'appointment': form.cleaned_data}})

    def form_invalid(self, form):
        print('Form invalid')
        print(form.errors)
        return super().form_invalid(form)

