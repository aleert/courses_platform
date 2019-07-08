from django.contrib.auth import get_user_model, login
from django.shortcuts import redirect
from rest_framework.reverse import reverse_lazy, reverse
from django.test import RequestFactory
from rest_registration.api.views.register import verify_registration as rest_verify_registration


def verify_registration(request):
    user_id = request.GET.get('user_id')
    timestamp = request.GET.get('timestamp')
    signature = request.GET.get('signature')
    backend_url = reverse('rest_registration:verify-registration')
    data = {
        'user_id': user_id,
        'timestamp': timestamp,
        'signature': signature
    }
    # make direct call to view instead of making actual POST request
    factory = RequestFactory()
    request_to_backend = factory.post(path=backend_url, data=data)
    response = rest_verify_registration(request_to_backend)

    if response.status_code == 200:
        # log-in user
        user_model = get_user_model()
        user = user_model.objects.get(pk=user_id)
        login(request, user)
        return redirect(reverse_lazy('courses:user_courses', args=[user_id, ]))
    else:
        # response 400
        return response
