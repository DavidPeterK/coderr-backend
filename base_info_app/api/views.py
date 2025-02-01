from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Avg, Sum
from offer_app.models import Offer
from user_auth_app.models import CustomUser


class BaseInfoView(APIView):
    def get(self, request, *args, **kwargs):
        # Anzahl der Bewertungen (Summe aller `review_count`-Felder)
        review_count = Offer.objects.aggregate(total_reviews=Sum('review_count'))[
            'total_reviews'] or 0

        # Durchschnittliche Bewertung (gewichteter Durchschnitt basierend auf den Bewertungen)
        average_rating = Offer.objects.aggregate(avg_rating=Avg('average_rating'))[
            'avg_rating'] or 0.0
        average_rating = round(average_rating, 1)

        # Anzahl der Geschäftsnutzer
        business_profile_count = CustomUser.objects.filter(
            type='business').count()

        # Anzahl der Angebote
        offer_count = Offer.objects.count()

        # Antwort erstellen
        data = {
            "review_count": review_count,
            "average_rating": average_rating,
            "business_profile_count": business_profile_count,
            "offer_count": offer_count,
        }
        return Response(data)
