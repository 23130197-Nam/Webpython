from rest_framework import serializers
from .models import Review, ReviewVote

class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.name', read_only=True)  # Flatten dữ liệu user
    
    class Meta:
        model = Review
        fields = ['id', 'user', 'username', 'rating', 'title', 'content', 'created_at', 'is_verified']
        read_only_fields = ['user', 'product', 'is_verified', 'created_at']

    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Rating phải từ 1 đến 5.")
        return value

class ReviewVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewVote
        fields = ['is_helpful']