from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Contact
from django.db.models import Q

class IdentifyView(APIView):
    def post(self, request):
        email = request.data.get('email')
        phone_number = request.data.get('phoneNumber')

        # Fetch matching contacts
        contacts = Contact.objects.filter(
            Q(email=email) | Q(phone_number=phone_number)
        )

        if contacts.exists():
            # LOGIC -> from the new record find all the records which have either same contact or same email id 
            # and then get their primary id's using linkedId, now we have to connect these primary ids into one 
            # using createdat which is have lower value would be primary and then change all the linkedId to the 
            # new primary key and now return the required things
            
            unique_linked_ids = set(contacts.filter(linked_id__isnull=False).values_list('linked_id', flat=True))
            unique_linked_ids.update(set(contacts.filter(link_precedence="primary").values_list('id', flat=True)))
            if(len(unique_linked_ids) == 2):
                contacts = Contact.objects.filter(id__in=unique_linked_ids)
                primary_contact = contacts.order_by('created_at').first()

                for contact in contacts:
                    if contact != primary_contact:
                        id = contact.id
                        contact.linked_id = primary_contact.id
                        contact.link_precedence = 'secondary'
                        contact.save()

                contacts = Contact.objects.filter(linked_id=id)

                for contact in contacts:
                    contact.linked_id = primary_contact.id
                    contact.save()
            else:
                no = unique_linked_ids.pop()
                primary_contact = Contact.objects.get(id=no)
            # Create a new contact -> When either email and phone no are not present that means new info
            if not Contact.objects.filter(Q(email=email)).exists() or not Contact.objects.filter(Q(phone_number=phone_number)).exists():
                new_contact = Contact.objects.create(
                    email=email,
                    phone_number=phone_number,
                    linked_id=primary_contact.id,
                    link_precedence='secondary'
                )
        else:
            primary_contact = Contact.objects.create(
                email=email,
                phone_number=phone_number,
                link_precedence='primary'
            )
            contacts = [primary_contact]

        contacts = Contact.objects.filter( Q(id=primary_contact.id) | Q(linked_id=primary_contact.id) )
        primary_email = primary_contact.email
        primary_phone_number = primary_contact.phone_number

        emails = list(set([contact.email for contact in contacts if contact.email and contact.email != primary_email]))
        phone_numbers = list(set([contact.phone_number for contact in contacts if contact.phone_number and contact.phone_number != primary_phone_number]))

        if(primary_email):
            emails = [primary_email] + emails
        if(primary_phone_number):
            phone_numbers = [primary_phone_number] + phone_numbers

        response_data = {
            "contact": {
                "primaryContactId": primary_contact.id,
                "emails": emails,
                "phoneNumbers": phone_numbers,
                "secondaryContactIds": [contact.id for contact in contacts if contact.id != primary_contact.id]
            }
        }

        return Response(response_data, status=status.HTTP_200_OK)
