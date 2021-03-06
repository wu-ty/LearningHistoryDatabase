from django.shortcuts import render_to_response
from django.template import RequestContext

from django.contrib.auth import authenticate, login, get_user_model

from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect, HttpResponse

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from django.contrib.auth import logout

from django.views import generic

from mysite.views import LoginRequiredMixin

from account.forms import UserForm, UserProfileForm
from account.models import UserProfile


# Create your views here.



def register(request):
    # Like before, get the request's context.
    context = RequestContext(request)

    # A boolean value for telling the template whether the registration was successful.
    # Set to False initially. Code changes value to True when registration succeeds.
    registered = False

    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
        # Attempt to grab information from the raw form information.
        # Note that we make use of both UserForm and UserProfileForm.
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        # If the two forms are valid...
        if user_form.is_valid() and profile_form.is_valid():
            # Save the user's form data to the database.
            user = user_form.save()

            # Now we hash the password with the set_password method.
            # Once hashed, we can update the user object.
            user.set_password(user.password)
            user.save()

            # Now sort out the UserProfile instance.
            # Since we need to set the user attribute ourselves, we set commit=False.
            # This delays saving the model until we're ready to avoid integrity problems.
            profile = profile_form.save(commit=False)
            profile.user = user

            # Now we save the UserProfile model instance.
            profile.save()

            # Update our variable to tell the template registration was successful.
            registered = True

        # Invalid form or forms - mistakes or something else?
        # Print problems to the terminal.
        # They'll also be shown to the user.
        else:
            print user_form.errors, profile_form.errors

    # Not a HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input.
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    # Render the template depending on the context.
    return render_to_response('account/register.html',{'user_form': user_form, 'profile_form': profile_form, 'registered': registered},context)




def user_login(request):
    # Like before, obtain the context for the user's request.
    context = RequestContext(request)

    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
        username = request.POST['username']
        password = request.POST['password']

        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)

        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                return HttpResponseRedirect(reverse('index'))
            else:
                # An inactive account was used - no logging in!
                return HttpResponse("Your account is disabled.")
        else:
            # Bad login details were provided. So we can't log the user in.
            print "Invalid login details: {0}, {1}".format(username, password)
            return HttpResponse("Invalid login details supplied.")

    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        return render_to_response('account/login.html', {}, context)





# Use the login_required() decorator to ensure only those logged in can access the view.
@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)

    # Take the user back to the homepage.
    return HttpResponseRedirect(reverse('index'))




class UserProfileDetailView(generic.DetailView):
    model = get_user_model()
    template_name = 'account/detail.html'
    slug_field = "username"
    context_object_name = 'user'

    def get_object(self, queryset=None):
        user = super(UserProfileDetailView, self).get_object(queryset)
        UserProfile.objects.get_or_create(user=user)
        return user
    
    
class UserProfileEditView(generic.edit.UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'account/update.html'

    def get_object(self, queryset=None):
        return UserProfile.objects.get_or_create(user=self.request.user)[0]

    def get_success_url(self):
        return reverse('account:detail', kwargs={'slug': self.request.user})



#class ProfileObjectMixin(generic.detail.SingleObjectMixin):
    #"""
    #Provides views with the current user's profile.
    #"""
    #model = UserProfile

    #def get_object(self):
        #"""Return's the current users profile."""
        #try:
            #return self.request.user.get_profile()
        #except UserProfile.DoesNotExist:
            #raise NotImplemented(
                #"What if the user doesn't have an associated profile?")

    #@method_decorator(login_required)
    #def dispatch(self, request, *args, **kwargs):
        #"""Ensures that only authenticated users can access the view."""
        #klass = ProfileObjectMixin
        #return super(klass, self).dispatch(request, *args, **kwargs)


#class ProfileUpdateView(ProfileObjectMixin, generic.edit.UpdateView):
    #"""
    #A view that displays a form for editing a user's profile.

    #Uses a form dynamically created for the `Profile` model and
    #the default model's update template.
    #"""
    ##form_class = UserProfileForm
    #context_object_name = 'userprofile'
    #template_name = 'account/detail.html'
