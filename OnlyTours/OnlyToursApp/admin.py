from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html
#register your models here

from .models import (
    Customer,
    CustomerTravelPreferences,
    TourGuide,
    LanguagesSpoken,
    Booking,
    Attractions,
    TourGuideRegistration,
    Listings,
    Payment,
    Review,
)


class CustomerTravelPreferencesInline(admin.TabularInline):
    
    model = CustomerTravelPreferences
    extra = 1                       
    max_num = 10
    fields = ('TravelPreferences',)
    verbose_name = "Travel preference"
    verbose_name_plural = "Travel preferences"
    show_change_link = True         


class LanguagesSpokenInline(admin.TabularInline):
    """Shows a Tour Guide's languages on the Tour Guide page."""
    model = LanguagesSpoken
    extra = 1
    max_num = 10
    fields = ('Language',)
    verbose_name = "Language spoken"
    verbose_name_plural = "Languages spoken"
    show_change_link = True



@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        'first_name',
        'last_name',
        'email',
        'CountryOfOrigin',
        'PrimaryLanguage',
        'date_joined',
        'booking_count',
    )
    list_display_links = ('first_name', 'last_name')
    list_filter = ('CountryOfOrigin', 'PrimaryLanguage')
    search_fields = ('first_name', 'last_name', 'email', 'PhoneNumber')
    ordering = ('last_name', 'first_name')
    list_per_page = 25
    date_hierarchy = 'date_joined'
    empty_value_display = '—'

    fieldsets = (
        ('Personal information', {
            'fields': ('first_name', 'last_name', 'email', 'PhoneNumber')
        }),
        ('Location & language', {
            'fields': ('CountryOfOrigin', 'PrimaryLanguage')
        }),
        ('Registration', {
            'fields': ('date_joined',),
        }),
    )

    inlines = [CustomerTravelPreferencesInline]

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(booking_count=Count('booking'))

    @admin.display(description='Bookings', ordering='booking_count')
    def booking_count(self, obj):
        return obj.booking_count



@admin.register(TourGuide)
class TourGuideAdmin(admin.ModelAdmin):
    list_display = (
        'first_name',
        'last_name',
        'email',
        'YearsofExperience',
        'PrimaryLanguage',
        'date_joined',
        'language_list',             
    )
    list_display_links = ('first_name', 'last_name')
    list_filter = ('PrimaryLanguage',)
    search_fields = ('first_name', 'last_name', 'email', 'PhoneNumber', 'Biography')
    ordering = ('last_name', 'first_name')
    list_per_page = 20
    date_hierarchy = 'date_joined'
    list_editable = ('YearsofExperience',)  
    empty_value_display = '—'

    fieldsets = (
        ('Personal information', {
            'fields': ('first_name', 'last_name', 'email', 'PhoneNumber')
        }),
        ('Guide profile', {
            'fields': ('YearsofExperience', 'PrimaryLanguage', 'Biography'),
            'description': 'Biography is capped at 30 characters in the model.',
        }),
        ('Registration', {
            'fields': ('date_joined',),
        }),
    )

    inlines = [LanguagesSpokenInline]

    actions = ['set_experience_to_zero']

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('languagesspoken_set')

    @admin.display(description='Languages')
    def language_list(self, obj):
        langs = [l.Language for l in obj.languagesspoken_set.all() if l.Language]
        return ", ".join(langs) or '—'

    @admin.action(description='Reset Years of Experience to 0 for selected guides')
    def set_experience_to_zero(self, request, queryset):
        updated = queryset.update(YearsofExperience=0)
        self.message_user(request, f"{updated} guide(s) updated.")



@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'BookingID',
        'Customer',
        'TourDate',
        'DateTimeRequested',
        'NumberOfParticipants',
        'TotalPrice',
        'colored_status',           
    )
    list_display_links = ('BookingID', 'Customer')
    list_filter = ('BookingStatus',)        
    search_fields = (
        'Customer__first_name',
        'Customer__last_name',
        'Customer__email',
    )
    ordering = ('-DateTimeRequested',)
    list_per_page = 25
    date_hierarchy = 'TourDate'             
    list_select_related = ('Customer',)     
    empty_value_display = '—'

    fieldsets = (
        ('Customer', {
            'fields': ('Customer',"Listing",),
        }),
        ('Booking dates', {
            'fields': ('TourDate','TimeSlot',),
        }),
        ('Booking details', {
            'fields': ('NumberOfParticipants', 'TotalPrice', 'BookingStatus',),
        }),
    )

    actions = ['mark_as_paid', 'mark_as_unpaid']

    @admin.display(description='Status', ordering='BookingStatus')
    def colored_status(self, obj):
        color = '#1a7f37' if obj.BookingStatus == 'PAID' else '#b42318'
        label = obj.get_BookingStatus_display().upper()
        return format_html(
            '<span style="color:{};font-weight:700;">{}</span>',
            color, label
        )

    @admin.action(description='Mark selected bookings as PAID')
    def mark_as_paid(self, request, queryset):
        updated = queryset.update(BookingStatus='PAID')
        self.message_user(request, f"{updated} booking(s) marked as paid.")

    @admin.action(description='Mark selected bookings as UNPAID')
    def mark_as_unpaid(self, request, queryset):
        updated = queryset.update(BookingStatus='UNPAID')
        self.message_user(request, f"{updated} booking(s) marked as unpaid.")



@admin.register(Attractions)
class AttractionsAdmin(admin.ModelAdmin):
    list_display = (
        'Name',
        'Region',
        'Type',
        'DifficultyLevel',
        'IsFeatured',
        'Distance',
        'DateAdded',
    )
    list_display_links = ('Name',)
    list_filter = (
        'IsFeatured',
        'Region',
        'Type',
        'DifficultyLevel',
    )
    search_fields = ('Name', 'Description', 'Region', 'Type')
    ordering = ('Name',)
    list_per_page = 20
    date_hierarchy = 'DateAdded'
    list_editable = ('IsFeatured',)    
    empty_value_display = '—'

    fieldsets = (
        ('Basic information', {
            'fields': ('Name', 'Description', 'Type', 'Region', 'Image')
        }),
        ('Classification', {
            'fields': ('DifficultyLevel', 'IsFeatured', 'Distance'),
        }),
        ('Location (decimal degrees)', {
            'fields': ('Latitude', 'Longitude'),
            'classes': ('collapse',),   
            'description': 'Coordinates are stored to 7 decimal places.',
        }),
        ('Meta', {
            'fields': ('DateAdded',),
        }),
    )

    
    radio_fields = {'DifficultyLevel': admin.HORIZONTAL}

    actions = ['feature_attractions', 'unfeature_attractions']

    @admin.action(description='Mark selected attractions as FEATURED')
    def feature_attractions(self, request, queryset):
        updated = queryset.update(IsFeatured=True)
        self.message_user(request, f"{updated} attraction(s) featured.")

    @admin.action(description='Mark selected attractions as NOT featured')
    def unfeature_attractions(self, request, queryset):
        updated = queryset.update(IsFeatured=False)
        self.message_user(request, f"{updated} attraction(s) unfeatured.")





@admin.register(CustomerTravelPreferences)
class CustomerTravelPreferencesAdmin(admin.ModelAdmin):
    list_display = ('id', 'Customer', 'TravelPreferences')
    list_filter = ('TravelPreferences',)
    search_fields = ('Customer__first_name', 'Customer__last_name', 'TravelPreferences')
    list_select_related = ('Customer',)
    ordering = ('Customer__last_name',)
    list_per_page = 25
    empty_value_display = '—'


@admin.register(LanguagesSpoken)
class LanguagesSpokenAdmin(admin.ModelAdmin):
    list_display = ('id', 'Guide', 'Language')
    list_filter = ('Language',)
    search_fields = ('Guide__first_name', 'Guide__last_name', 'Language')
    list_select_related = ('Guide',)
    ordering = ('Language',)
    list_per_page = 25
    empty_value_display = '—'

@admin.register(TourGuideRegistration)
class TourGuideRegistrationAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'Guide',
        'DocumentType',
        'SubmissionDate',
        'RegistrationStatus',
        'RejectionReason',
    )
    list_display_links = ('id', 'Guide')
    list_filter = ('RegistrationStatus', 'DocumentType')
    search_fields = (
        'Guide__first_name',
        'Guide__last_name',
        'Guide__Email',
        'DocumentType',
    )
    ordering = ('-SubmissionDate',)
    list_per_page = 25
    date_hierarchy = 'SubmissionDate'
    list_select_related = ('Guide',)
    empty_value_display = '—'

    fieldsets = (
        ('Guide', {
            'fields': ('Guide',)
        }),
        ('Document', {
            'fields': ('DocumentType', 'SubmissionDate'),
        }),
        ('Status', {
            'fields': ('RegistrationStatus', 'RejectionReason'),
        }),
    )

    radio_fields = {'RegistrationStatus': admin.HORIZONTAL}

    actions = ['mark_as_approved', 'mark_as_rejected', 'mark_as_pending']

    @admin.action(description='Mark selected registrations as APPROVED')
    def mark_as_approved(self, request, queryset):
        updated = queryset.update(RegistrationStatus='APPROVED', RejectionReason=None)
        self.message_user(request, f"{updated} registration(s) approved.")

    @admin.action(description='Mark selected registrations as REJECTED')
    def mark_as_rejected(self, request, queryset):
        updated = queryset.update(RegistrationStatus='REJECTED')
        self.message_user(request, f"{updated} registration(s) rejected.")

    @admin.action(description='Mark selected registrations as PENDING')
    def mark_as_pending(self, request, queryset):
        updated = queryset.update(RegistrationStatus='PENDING', RejectionReason=None)
        self.message_user(request, f"{updated} registration(s) reset to pending.")


@admin.register(Listings)
class ListingsAdmin(admin.ModelAdmin):
    list_display = (
        'ListingID',
        'TourName',
        'Guide',
        'Duration',
        'Price',
        'AvailabilityDate',
        'ListingsStatus',
        'DateCreated',
    )
    list_display_links = ('ListingID', 'TourName')
    list_filter = ('ListingsStatus', 'AvailabilityDate')
    search_fields = ('TourName', 'LDescription', 'MeetingPoint', 'Guide__first_name', 'Guide__last_name')
    ordering = ('-DateCreated',)
    list_per_page = 20
    date_hierarchy = 'AvailabilityDate'
    list_select_related = ('Guide',)
    list_editable = ('ListingsStatus',)
    empty_value_display = '—'

    fieldsets = (
        ('Guide', {
            'fields': ('Guide',)
        }),
        ('Tour information', {
            'fields': ('TourName', 'LDescription', 'Duration', 'MeetingPoint', 'Price'),
        }),
        ('Availability & status', {
            'fields': ('AvailabilityDate', 'ListingsStatus',),
        }),
    )

    radio_fields = {'ListingsStatus': admin.HORIZONTAL}

    actions = ['activate_listings', 'deactivate_listings']

    @admin.action(description='Mark selected listings as ACTIVE')
    def activate_listings(self, request, queryset):
        updated = queryset.update(ListingsStatus='ACTIVE')
        self.message_user(request, f"{updated} listing(s) activated.")

    @admin.action(description='Mark selected listings as INACTIVE')
    def deactivate_listings(self, request, queryset):
        updated = queryset.update(ListingsStatus='INACTIVE')
        self.message_user(request, f"{updated} listing(s) deactivated.")




@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'PaymentID',
        'BookingID',
        'Amount',
        'Currency',
        'PaymentStatus',
        'PaymentMethod',
        'TransactionDate',
        'colored_payment_status',
    )
    list_display_links = ('PaymentID', 'BookingID')
    list_filter = ('PaymentStatus', 'PaymentMethod', 'Currency')
    search_fields = (
        'BookingID__Customer__first_name',
        'BookingID__Customer__last_name',
        'PaymentMethod',
        'Currency',
    )
    ordering = ('-TransactionDate',)
    list_per_page = 25
    date_hierarchy = 'TransactionDate'
    list_select_related = ('BookingID',)
    list_editable = ('PaymentStatus',)
    empty_value_display = '—'

    fieldsets = (
        ('Booking', {
            'fields': ('BookingID',)
        }),
        ('Payment details', {
            'fields': ('Amount', 'Currency', 'ExchangeRate', 'PaymentMethod'),
        }),
        ('Status & date', {
            'fields': ('PaymentStatus', 'TransactionDate'),
        }),
    )

    @admin.display(description='Status', ordering='PaymentStatus')
    def colored_payment_status(self, obj):
        if not obj.PaymentStatus:
            return '—'
        status = obj.PaymentStatus.upper()
        color = '#1a7f37' if status == 'PAID' else '#b42318' if status == 'FAILED' else '#b54708'
        return format_html(
            '<span style="color:{};font-weight:700;">{}</span>',
            color, status
        )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'ReviewID',
        'Booking',
        'star_rating',
        'short_comment',
        'DateSubmitted',
        'IsFlagged',
        'has_guide_response',
    )
    list_display_links = ('ReviewID', 'Booking')
    list_filter = ('IsFlagged', 'Rating', 'DateSubmitted')
    search_fields = ('Comment', 'GuideResponse')
    ordering = ('-DateSubmitted',)
    list_per_page = 25
    date_hierarchy = 'DateSubmitted'
    list_select_related = ('Booking',)
    list_editable = ('IsFlagged',)
    empty_value_display = '—'

    readonly_fields = ('DateSubmitted',)

    fieldsets = (
        ('Review', {
            'fields': ('Booking', 'Rating', 'Comment')
        }),
        ('Moderation', {
            'fields': ('IsFlagged',),
        }),
        ('Guide response', {
            'fields': ('GuideResponse',),
        }),
        ('Meta', {
            'fields': ('DateSubmitted',),
        }),
    )

    actions = ['flag_reviews', 'unflag_reviews']

    @admin.display(description='Rating', ordering='Rating')
    def star_rating(self, obj):
        return '★' * obj.Rating + '☆' * (5 - obj.Rating)

    @admin.display(description='Comment')
    def short_comment(self, obj):
        if not obj.Comment:
            return '—'
        return obj.Comment[:50] + ('…' if len(obj.Comment) > 50 else '')

    @admin.display(boolean=True, description='Guide replied?')
    def has_guide_response(self, obj):
        return bool(obj.GuideResponse)

    @admin.action(description='Flag selected reviews')
    def flag_reviews(self, request, queryset):
        updated = queryset.update(IsFlagged=True)
        self.message_user(request, f"{updated} review(s) flagged.")

    @admin.action(description='Remove flag from selected reviews')
    def unflag_reviews(self, request, queryset):
        updated = queryset.update(IsFlagged=False)
        self.message_user(request, f"{updated} review(s) unflagged.")

