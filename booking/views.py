from django.shortcuts import render, redirect
from datetime import date, datetime, timedelta
from .models import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator

# homepage
def index(request):
    return render(request, "booking/index.html", {})

# menu page
def menu(request):
    return render(request, "booking/menu.html", {})

# first page of table booking form (table and day of booking)
def table_booking(request):
    user = request.user
    days_open = valid_day(22)
    validate_days = is_day_valid(days_open)
    if user.is_authenticated:
        if request.method == 'POST':
            table = request.POST.get('table')
            day = request.POST.get('day')
            if table is None:
                messages.success(request, "Please Select Your Table!")
                return redirect('table_booking')
            request.session['day'] = day
            request.session['table'] = table
            return redirect('table_booking_submit')
        return render(request, 'booking/table_booking.html', {
            'days_open': days_open,
            'validate_days': validate_days
        })
    else:
        messages.success(request, "Please log-in to book a table.")
        return redirect('login_user')

# second page of table booking form (time and special requirements)
def table_booking_submit(request):
    user = request.user
    times = [
        "1 PM", "3 PM", "5 PM", "7 PM", "9 PM"
    ]
    today = datetime.now()
    tomorrow = today + timedelta(days=1)
    min_date = tomorrow.strftime('%Y-%m-%d')
    deltatime = tomorrow + timedelta(days=21)
    strdeltatime = deltatime.strftime('%Y-%m-%d')
    max_date = strdeltatime
    day = request.session.get('day')
    table = request.session.get('table')
    special_requirements = request.session.get('special_requirements')
    available_times = check_time(times, day, table)
    if user.is_authenticated:
        if request.method == 'POST':
            time = request.POST.get("time")
            special_requirements = request.POST.get("special_requirements")
            date = day_to_day_open(day)
            if table is not None:
                if day <= max_date and day >= min_date:
                    if date == 'Thursday' or date == 'Friday' or date == 'Saturday' or date == 'Sunday':  # noqa
                        if Table_Booking.objects.filter(day=day).count() < 40:
                            if time in available_times:
                                Table_Booking_Form = Table_Booking.objects.get_or_create(  # noqa
                                   user=user,
                                   table=table,
                                   day=day,
                                   time=time,
                                   special_requirements=special_requirements
                                )
                                messages.success(request,
                                                 "Your table booking has been made!")  # noqa
                                days_open = valid_day(22)
                                validate_days = is_day_valid(days_open)
                                return redirect('user_panel')
                            else:
                                messages.success(request,
                                                 "This booking is not available!")  # noqa
                                days_open = valid_day(22)
                                validate_days = is_day_valid(days_open)
                                return render(request,
                                              'booking/table_booking.html', {
                                               'days_open': days_open,
                                               'validate_days': validate_days,
                                              })
                        else:
                            messages.success(request,
                                             "The selected day is now full!")
                            days_open = valid_day(22)
                            validate_days = is_day_valid(days_open)
                            return render(request,
                                          'booking/table_booking.html', {
                                           'days_open': days_open,
                                           'validate_days': validate_days,
                                          })
                    else:
                        messages.success(request,
                                         "Sorry we're not open on that day!")
                        days_open = valid_day(22)
                        validate_days = is_day_valid(days_open)
                        return render(request, 'booking/table_booking.html', {
                            'days_open': days_open,
                            'validate_days': validate_days,
                        })
                else:
                    messages.success(request,
                                     "That day isn't available right now!")
                    days_open = valid_day(22)
                    validate_days = is_day_valid(days_open)
                    return render(request, 'booking/table_booking.html', {
                        'days_open': days_open,
                        'validate_days': validate_days,
                    })
            else:
                messages.success(request,
                                 "Please select a table first!")
                days_open = valid_day(22)
                validate_days = is_day_valid(days_open)
                return render(request, 'booking/table_booking.html', {
                    'days_open': days_open,
                    'validate_days': validate_days,
                })
        if not available_times:
            messages.warning(request, "That booking is no longer available.")
            days_open = valid_day(22)
            validate_days = is_day_valid(days_open)
            return render(request, 'booking/table_booking.html', {
                'days_open': days_open,
                'validate_days': validate_days,
            })
        return render(request, 'booking/table_booking_submit.html', {
                'times': available_times,
                'special_requirements': special_requirements,
        })
    else:
        messages.success(request, 'Please sign in to make a table booking.')
        return redirect('login_user')

# user bookings page
def user_panel(request):
    user = request.user
    if user.is_authenticated:
        current_date = datetime.now().date()
        bookings = Table_Booking.objects.filter(user=user, day__gte=current_date).order_by('day', 'time')  # noqa
        p = Paginator(bookings, 1)
        today = date.today()
        page = request.GET.get('page')
        table_bookings = p.get_page(page)
        return render(request, 'booking/user_panel.html', {
            'user': user,
            'bookings': bookings,
            'table_bookings': table_bookings,
            'today': today,
        })
    else:
        messages.success(request, 'Please sign in to view your bookings.')
        return redirect('login_user')

# first page of the update booking form (table and day)
def user_update(request, id):
    table_booking = Table_Booking.objects.get(pk=id)
    user_date_selected = table_booking.day
    today = datetime.today()
    tomorrow = today + timedelta(days=1)
    min_deletion_date = tomorrow
    days_open = valid_day(22)
    validate_days = is_day_valid(days_open)
    if request.user.is_authenticated:
        if request.user == table_booking.user:
            if user_date_selected >= min_deletion_date.date():
                if request.method == 'POST':
                    table = request.POST.get('table')
                    day = request.POST.get('day')
                    request.session['day'] = day
                    request.session['table'] = table
                    return redirect('user_update_submit', id=id)
            else:
                messages.error(request,
                                "Editing bookings is only available on the days before your booking!")  # noqa
                return redirect('user_panel')
        else:
            messages.success(request,
                             "This isn't your booking, so can't do that!")
            return render(request, 'booking/index.html')
        return render(request, 'booking/user_update.html', {
                'days_open': days_open,
                'validate_days': validate_days,
                'id': id,
            })
    else:
        messages.success(request, 'Please sign in to view your bookings.')
        return redirect('login_user')

# second page of the update booking form (time and special requirements)
def user_update_submit(request, id):
    user = request.user
    times = [
        "1 PM", "3 PM", "5 PM", "7 PM", "9 PM"
    ]
    table_booking = Table_Booking.objects.get(pk=id)
    today = datetime.now()
    tomorrow = today + timedelta(days=1)
    user_date_selected = table_booking.day
    min_date = tomorrow.strftime('%Y-%m-%d')
    delta24 = (user_date_selected).strftime('%Y-%m-%d') >= min_date
    deltatime = tomorrow + timedelta(days=21)
    strdeltatime = deltatime.strftime('%Y-%m-%d')
    max_date = strdeltatime
    day = request.session.get('day')
    table = request.session.get('table')
    special_requirements = request.session.get('special_requirements')
    hour = check_edit_time(times, day, id)
    user_selected_time = table_booking.time
    if user == table_booking.user:
        if delta24:
            if request.method == 'POST':
                time = request.POST.get("time")
                special_requirements = request.POST.get("special_requirements")
                date = day_to_day_open(day)
                if table is not None:
                    if day <= max_date and day >= min_date:
                        if date == 'Thursday' or date == 'Friday' or date == 'Saturday' or date == 'Sunday':  # noqa
                            if Table_Booking.objects.filter(day=day).count() < 40:  # noqa
                                if Table_Booking.objects.filter(day=day, time=time).count() < 1 or user_selected_time == time:  # noqa
                                    Table_Booking_Form = Table_Booking.objects.filter(pk=id).update(  # noqa
                                        user=user,
                                        table=table,
                                        day=day,
                                        time=time,
                                        special_requirements=special_requirements,  # noqa
                                        )
                                    messages.success(request,
                                                     "Your booking has been updated!")  # noqa
                                    return redirect('user_panel')
                                else:
                                    messages.error(request,
                                                   "That time is taken!")
                                    return redirect('user_panel')
                            else:
                                messages.error(request,
                                               "This day is fully booked!")
                                return redirect('user_panel')
                        else:
                            messages.error(request,
                                           "We're not open on that day!")
                            return redirect('user_panel')
                    else:
                        messages.error(request,
                                       "Sorry no bookings for that date!")
                        return redirect('user_panel')
                else:
                    messages.error(request,
                                   "Please select a table first!")
                return redirect('user_panel')
            return render(request, 'booking/user_update_submit.html', {
                'times': hour,
                'id': id,
                'special_requirements': special_requirements,
            })
        else:
            messages.error(request,
                           "Editing bookings is only available on the days before your booking!")  # noqa
            return redirect('user_panel')
    else:
        messages.error(request,
                       "That's not your booking, so you can't do that.")
        return render(request, 'booking/index.html')

# customer bookings page
def staff_panel(request):
    user = request.user
    today = datetime.today()
    min_date = today.strftime('%Y-%m-%d')
    deltatime = today + timedelta(days=22)
    strdeltatime = deltatime.strftime('%Y-%m-%d')
    max_date = strdeltatime
    if user.is_authenticated and user.is_superuser:
        items = Table_Booking.objects.filter(day__range=[min_date, max_date]).order_by('day', 'time')  # noqa
        return render(request, 'booking/staff_panel.html', {
            'items': items,
        })
    else:
        messages.error(request, "You are not authorised to view that page.")
        return redirect('index')

# checks if a date is given and returns a day
def day_to_day_open(x):
    if x is None:
        return None
    else:
        z = datetime.strptime(x, "%Y-%m-%d")
        y = z.strftime('%A')
        return y

# takes days and finds these as dates i.e. when the bar is open
def valid_day(days):
    today = datetime.now()
    tomorrow = today + timedelta(days=1)
    valid_days = []
    for i in range(0, days):
        x = tomorrow + timedelta(days=i)
        y = x.strftime('%A')
        if y == 'Thursday' or y == 'Friday' or y == 'Saturday' or y == 'Sunday':  # noqa
            valid_days.append(x.strftime('%Y-%m-%d'))
    return valid_days

# checks the day has less than the total possible bookings
def is_day_valid(x):
    validate_days = []
    for j in x:
        if Table_Booking.objects.filter(day=j).count() < 40:
            validate_days.append(j)
    return validate_days

# checks availability and returns available times
def check_time(times, day, table):
    bookings = Table_Booking.objects.filter(day=day)
    available_times = []
    for time in times:
        booking_exists = bookings.filter(time=time, table=table).exists()
        if not booking_exists:
            available_times.append(time)
    return available_times

# checks availability and returns available times for the update booking form  
def check_edit_time(times, day, id):
    x = []
    table_booking = Table_Booking.objects.get(pk=id)
    time = table_booking.time
    for k in times:
        if Table_Booking.objects.filter(day=day, time=k).count() < 1 or time == k:  # noqa
            x.append(k)
    return x

# deletes a booking
def delete_booking(request, booking_id):
    table_booking = Table_Booking.objects.get(pk=booking_id)
    if request.user.is_authenticated:
        if request.user == table_booking.user:
            today = datetime.today()
            tomorrow = today + timedelta(days=1)
            booking_date = table_booking.day
            min_deletion_date = tomorrow
            if booking_date >= min_deletion_date.date():
                Table_Booking.objects.get(pk=booking_id).delete()
                messages.success(request, ("Booking successfully cancelled!"))
                return redirect('user_panel')
            else:
                messages.error(request,
                               "Cancelling bookings is only available on the days before your booking!")  # noqa
                return redirect('user_panel')
        else:
            messages.error(request, ("You aren't authorised to do that!"))
            return redirect('user_panel')
    else:
        messages.error(request, ("Please log-in to delete your bookings"))
        return redirect('index')
