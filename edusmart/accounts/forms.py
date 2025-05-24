# from django import forms
# from django.contrib.auth.forms import UserCreationForm
# from django.core.exceptions import ValidationError
# from django.utils import timezone
# from .models import CustomUser, AdminInviteToken

# class CustomUserCreationForm(UserCreationForm):
#     email = forms.EmailField(
#         required=True,
#         widget=forms.EmailInput(attrs={'class': 'w-full p-2 border rounded', 'placeholder': 'Email'})
#     )
#     user_type = forms.ChoiceField(
#         choices=[('', 'Select User Type')] + list(CustomUser.USER_TYPE_CHOICES),
#         required=True,
#         widget=forms.Select(attrs={'class': 'w-full p-2 border rounded'})
#     )
#     roll_number = forms.CharField(
#         max_length=50,
#         required=False,
#         widget=forms.TextInput(attrs={'class': 'w-full p-2 border rounded', 'placeholder': 'Roll Number (Students)'})
#     )
#     department = forms.CharField(
#         max_length=100,
#         required=False,
#         widget=forms.TextInput(attrs={'class': 'w-full p-2 border rounded', 'placeholder': 'Department (Teachers)'})
#     )
#     designation = forms.CharField(
#         max_length=100,
#         required=False,
#         widget=forms.TextInput(attrs={'class': 'w-full p-2 border rounded', 'placeholder': 'Designation (Teachers)'})
#     )
#     course = forms.CharField(
#         max_length=100,
#         required=False,
#         widget=forms.TextInput(attrs={'class': 'w-full p-2 border rounded', 'placeholder': 'Course (Students)'})
#     )
#     branch = forms.CharField(
#         max_length=100,
#         required=False,
#         widget=forms.TextInput(attrs={'class': 'w-full p-2 border rounded', 'placeholder': 'Branch (Students)'})
#     )
#     profile_picture = forms.ImageField(
#         required=False,
#         widget=forms.FileInput(attrs={'class': 'w-full p-2 border rounded'})
#     )
#     bio = forms.CharField(
#         widget=forms.Textarea(attrs={'class': 'w-full p-2 border rounded', 'placeholder': 'Bio'}),
#         required=False
#     )
#     admin_token = forms.CharField(
#         max_length=100,
#         required=False,
#         label="Admin Invite Token",
#         widget=forms.TextInput(attrs={'class': 'w-full p-2 border rounded', 'placeholder': 'Admin Invite Token (Admins)'})
#     )

#     class Meta:
#         model = CustomUser
#         fields = ('username', 'email', 'password1', 'password2', 'user_type', 'roll_number', 'department',
#                   'designation', 'course', 'branch', 'profile_picture', 'bio', 'admin_token')

#     def clean(self):
#         cleaned_data = super().clean()
#         user_type = cleaned_data.get('user_type')
#         roll_number = cleaned_data.get('roll_number')
#         department = cleaned_data.get('department')
#         designation = cleaned_data.get('designation')
#         admin_token = cleaned_data.get('admin_token')
#         course = cleaned_data.get('course')
#         branch = cleaned_data.get('branch')

#         if user_type == 'student':
#             if not roll_number:
#                 self.add_error('roll_number', 'Roll number is required for students.')
#             if not course:
#                 self.add_error('course', 'Course is required for students.')
#             if not branch:
#                 self.add_error('branch', 'Branch is required for students.')
#         elif user_type == 'teacher':
#             if not department:
#                 self.add_error('department', 'Department is required for teachers.')
#             if not designation:
#                 self.add_error('designation', 'Designation is required for teachers.')
#         elif user_type == 'admin':
#             if not admin_token:
#                 self.add_error('admin_token', 'Admin invite token is required.')
#             else:
#                 try:
#                     token = AdminInviteToken.objects.get(token=admin_token, used=False, expires_at__gt=timezone.now())
#                     if not token.is_valid():
#                         self.add_error('admin_token', 'Invalid or expired admin invite token.')
#                 except AdminInviteToken.DoesNotExist:
#                     self.add_error('admin_token', 'Invalid admin invite token.')
#         return cleaned_data

#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user_type = self.cleaned_data['user_type']
#         user.user_type = user_type
#         if user_type == 'admin':
#             user.is_staff = True  # Admins have staff access
#             user.is_email_verified = False
#             # Do not mark token as used to allow multiple signups
#             # token = AdminInviteToken.objects.get(token=self.cleaned_data['admin_token'])
#             # token.used = True
#             # token.save()
#         user.roll_number = self.cleaned_data.get('roll_number') or None
#         user.department = self.cleaned_data.get('department') or None
#         user.designation = self.cleaned_data.get('designation') or None
#         user.course = self.cleaned_data.get('course') or None
#         user.branch = self.cleaned_data.get('branch') or None
#         user.bio = self.cleaned_data.get('bio') or None
#         if commit:
#             user.save()
#         return user

# class ProfileUpdateForm(forms.ModelForm):
#     email = forms.EmailField(
#         required=True,
#         widget=forms.EmailInput(attrs={'class': 'w-full p-2 border rounded'})
#     )
#     user_type = forms.ChoiceField(
#         choices=CustomUser.USER_TYPE_CHOICES,
#         required=True,
#         widget=forms.Select(attrs={'class': 'w-full p-2 border rounded'})
#     )
#     roll_number = forms.CharField(
#         max_length=50,
#         required=False,
#         widget=forms.TextInput(attrs={'class': 'w-full p-2 border rounded'})
#     )
#     department = forms.CharField(
#         max_length=100,
#         required=False,
#         widget=forms.TextInput(attrs={'class': 'w-full p-2 border rounded'})
#     )
#     designation = forms.CharField(
#         max_length=100,
#         required=False,
#         widget=forms.TextInput(attrs={'class': 'w-full p-2 border rounded'})
#     )
#     course = forms.CharField(
#         max_length=100,
#         required=False,
#         widget=forms.TextInput(attrs={'class': 'w-full p-2 border rounded'})
#     )
#     branch = forms.CharField(
#         max_length=100,
#         required=False,
#         widget=forms.TextInput(attrs={'class': 'w-full p-2 border rounded'})
#     )
#     profile_picture = forms.ImageField(
#         required=False,
#         widget=forms.FileInput(attrs={'class': 'w-full p-2 border rounded'})
#     )
#     bio = forms.CharField(
#         widget=forms.Textarea(attrs={'class': 'w-full p-2 border rounded'}),
#         required=False
#     )

#     class Meta:
#         model = CustomUser
#         fields = ('username', 'email', 'user_type', 'roll_number', 'department',
#                   'designation', 'course', 'branch', 'profile_picture', 'bio')

#     def __init__(self, *args, **kwargs):
#         self.request = kwargs.pop('request', None)
#         super().__init__(*args, **kwargs)
#         # Restrict user_type changes for non-admins
#         if self.request and self.request.user.user_type != 'admin':
#             self.fields['user_type'].disabled = True
#         # Set field requirements based on user_type
#         if self.instance.user_type == 'student':
#             self.fields['roll_number'].required = True
#             self.fields['course'].required = True
#             self.fields['branch'].required = True
#             self.fields['department'].widget = forms.HiddenInput()
#             self.fields['designation'].widget = forms.HiddenInput()
#         elif self.instance.user_type == 'teacher':
#             self.fields['department'].required = True
#             self.fields['designation'].required = True
#             self.fields['roll_number'].widget = forms.HiddenInput()
#             self.fields['course'].widget = forms.HiddenInput()
#             self.fields['branch'].widget = forms.HiddenInput()
#         else:  # admin
#             self.fields['roll_number'].widget = forms.HiddenInput()
#             self.fields['department'].widget = forms.HiddenInput()
#             self.fields['designation'].widget = forms.HiddenInput()
#             self.fields['course'].widget = forms.HiddenInput()
#             self.fields['branch'].widget = forms.HiddenInput()

#     def clean(self):
#         cleaned_data = super().clean()
#         user_type = cleaned_data.get('user_type')
#         roll_number = cleaned_data.get('roll_number')
#         department = cleaned_data.get('department')
#         designation = cleaned_data.get('designation')
#         course = cleaned_data.get('course')
#         branch = cleaned_data.get('branch')

#         if user_type == 'student':
#             if not roll_number:
#                 self.add_error('roll_number', 'Roll number is required for students.')
#             if not course:
#                 self.add_error('course', 'Course is required for students.')
#             if not branch:
#                 self.add_error('branch', 'Branch is required for students.')
#         elif user_type == 'teacher':
#             if not department:
#                 self.add_error('department', 'Department is required for teachers.')
#             if not designation:
#                 self.add_error('designation', 'Designation is required for teachers.')
#         return cleaned_data
























from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import CustomUser, AdminInviteToken

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'w-full p-2 border rounded', 'placeholder': 'Email'})
    )
    user_type = forms.ChoiceField(
        choices=[('', 'Select User Type')] + list(CustomUser.USER_TYPE_CHOICES),
        required=True,
        widget=forms.Select(attrs={'class': 'w-full p-2 border rounded'})
    )
    roll_number = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'w-full p-2 border rounded', 'placeholder': 'Roll Number (Students)'})
    )
    department = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'w-full p-2 border rounded', 'placeholder': 'Department (Teachers)'})
    )
    designation = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'w-full p-2 border rounded', 'placeholder': 'Designation (Teachers)'})
    )
    course = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'w-full p-2 border rounded', 'placeholder': 'Course (Students)'})
    )
    branch = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'w-full p-2 border rounded', 'placeholder': 'Branch (Students)'})
    )
    profile_picture = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'w-full p-2 border rounded'})
    )
    bio = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'w-full p-2 border rounded', 'placeholder': 'Bio'}),
        required=False
    )
    admin_token = forms.CharField(
        max_length=100,
        required=False,
        label="Admin Invite Token",
        widget=forms.TextInput(attrs={'class': 'w-full p-2 border rounded', 'placeholder': 'Admin Invite Token (Admins)'})
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'user_type', 'roll_number', 'department',
                  'designation', 'course', 'branch', 'profile_picture', 'bio', 'admin_token')

    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get('user_type')
        roll_number = cleaned_data.get('roll_number')
        department = cleaned_data.get('department')
        designation = cleaned_data.get('designation')
        admin_token = cleaned_data.get('admin_token')
        course = cleaned_data.get('course')
        branch = cleaned_data.get('branch')

        if user_type == 'student':
            if not roll_number:
                self.add_error('roll_number', 'Roll number is required for students.')
            if not course:
                self.add_error('course', 'Course is required for students.')
            if not branch:
                self.add_error('branch', 'Branch is required for students.')
        elif user_type == 'teacher':
            if not department:
                self.add_error('department', 'Department is required for teachers.')
            if not designation:
                self.add_error('designation', 'Designation is required for teachers.')
        elif user_type == 'admin':
            if not admin_token:
                self.add_error('admin_token', 'Admin invite token is required.')
            else:
                try:
                    token = AdminInviteToken.objects.get(token=admin_token, used=False, expires_at__gt=timezone.now())
                    if not token.is_valid():
                        self.add_error('admin_token', 'Invalid or expired admin invite token.')
                except AdminInviteToken.DoesNotExist:
                    self.add_error('admin_token', 'Invalid admin invite token.')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user_type = self.cleaned_data['user_type']
        user.user_type = user_type
        if user_type == 'admin':
            user.is_staff = True
            user.is_sub_admin = True  # Mark as sub-admin
            user.is_email_verified = True  # Auto-verify for invite-based signup
            token = AdminInviteToken.objects.get(token=self.cleaned_data['admin_token'])
            token.used = True  # Mark token as used
            token.save()
        user.roll_number = self.cleaned_data.get('roll_number') or None
        user.department = self.cleaned_data.get('department') or None
        user.designation = self.cleaned_data.get('designation') or None
        user.course = self.cleaned_data.get('course') or None
        user.branch = self.cleaned_data.get('branch') or None
        user.bio = self.cleaned_data.get('bio') or None
        if commit:
            user.save()
        return user

class SubAdminCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'w-full p-2 border rounded', 'placeholder': 'Email'})
    )
    profile_picture = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'w-full p-2 border rounded'})
    )
    bio = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'w-full p-2 border rounded', 'placeholder': 'Bio'}),
        required=False
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'profile_picture', 'bio')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError('This email is already in use.')
        return email

class ProfileUpdateForm(forms.ModelForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'w-full p-2 border rounded'})
    )
    user_type = forms.ChoiceField(
        choices=CustomUser.USER_TYPE_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'w-full p-2 border rounded'})
    )
    roll_number = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'w-full p-2 border rounded'})
    )
    department = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'w-full p-2 border rounded'})
    )
    designation = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'w-full p-2 border rounded'})
    )
    course = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'w-full p-2 border rounded'})
    )
    branch = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'w-full p-2 border rounded'})
    )
    profile_picture = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'w-full p-2 border rounded'})
    )
    bio = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'w-full p-2 border rounded'}),
        required=False
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'user_type', 'roll_number', 'department',
                  'designation', 'course', 'branch', 'profile_picture', 'bio')

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        # Restrict user_type changes for non-admins
        if self.request and self.request.user.user_type != 'admin':
            self.fields['user_type'].disabled = True
        # Set field requirements based on user_type
        if self.instance.user_type == 'student':
            self.fields['roll_number'].required = True
            self.fields['course'].required = True
            self.fields['branch'].required = True
            self.fields['department'].widget = forms.HiddenInput()
            self.fields['designation'].widget = forms.HiddenInput()
        elif self.instance.user_type == 'teacher':
            self.fields['department'].required = True
            self.fields['designation'].required = True
            self.fields['roll_number'].widget = forms.HiddenInput()
            self.fields['course'].widget = forms.HiddenInput()
            self.fields['branch'].widget = forms.HiddenInput()
        else:  # admin
            self.fields['roll_number'].widget = forms.HiddenInput()
            self.fields['department'].widget = forms.HiddenInput()
            self.fields['designation'].widget = forms.HiddenInput()
            self.fields['course'].widget = forms.HiddenInput()
            self.fields['branch'].widget = forms.HiddenInput()

    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get('user_type')
        roll_number = cleaned_data.get('roll_number')
        department = cleaned_data.get('department')
        designation = cleaned_data.get('designation')
        course = cleaned_data.get('course')
        branch = cleaned_data.get('branch')

        if user_type == 'student':
            if not roll_number:
                self.add_error('roll_number', 'Roll number is required for students.')
            if not course:
                self.add_error('course', 'Course is required for students.')
            if not branch:
                self.add_error('branch', 'Branch is required for students.')
        elif user_type == 'teacher':
            if not department:
                self.add_error('department', 'Department is required for teachers.')
            if not designation:
                self.add_error('designation', 'Designation is required for teachers.')
        return cleaned_data