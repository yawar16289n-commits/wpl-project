'use client';

import { useState, useEffect } from 'react';
import { reviewApi, ratingApi } from '@/lib/api';
import { canReview } from '@/lib/auth';

interface Review {
  id: number;
  user_id: number;
  user_name: string;
  comment: string;
  created_at: string;
}

interface Rating {
  id: number;
  user_id: number;
  rating: number;
}

interface ReviewsRatingsProps {
  courseId: number;
  userId: number | null;
  isEnrolled: boolean;
}

export default function ReviewsRatings({ courseId, userId, isEnrolled }: ReviewsRatingsProps) {
  const [reviews, setReviews] = useState<Review[]>([]);
  const [userRating, setUserRating] = useState<number>(0);
  const [userRatingId, setUserRatingId] = useState<number | null>(null);
  const [newReview, setNewReview] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [hoveredStar, setHoveredStar] = useState(0);

  useEffect(() => {
    fetchReviews();
    if (userId) {
      fetchUserRating();
    }
  }, [courseId, userId]);

  const fetchReviews = async () => {
    const response = await reviewApi.getCourseReviews(courseId);
    if (response.success && response.data) {
      const data = response.data as { reviews: Review[] };
      setReviews(data.reviews || []);
    }
  };

  const fetchUserRating = async () => {
    if (!userId) return;
    const response = await ratingApi.getUserRating(userId, courseId);
    if (response.success && response.data) {
      const data = response.data as { rating?: Rating };
      if (data.rating) {
        setUserRating(data.rating.rating);
        setUserRatingId(data.rating.id);
      }
    }
  };

  const handleRatingClick = async (rating: number) => {
    if (!userId || !isEnrolled) return;
    
    if (!canReview()) {
      alert('Instructors cannot submit ratings. Only students and admins can rate courses.');
      return;
    }

    setUserRating(rating);
    
    // createRating handles both create and update
    const response = await ratingApi.createRating(courseId, userId, rating);
    if (response.success && response.data) {
      const data = response.data as { rating: Rating };
      setUserRatingId(data.rating.id);
    }
  };

  const handleReviewSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!userId || !newReview.trim() || !isEnrolled) return;
    
    if (!canReview()) {
      alert('Instructors cannot submit reviews. Only students and admins can review courses.');
      return;
    }

    setSubmitting(true);
    const response = await reviewApi.createReview(courseId, userId, newReview);
    
    if (response.success) {
      setNewReview('');
      fetchReviews();
    }
    
    setSubmitting(false);
  };

  return (
    <div className="space-y-8">
      {userId && isEnrolled && canReview() && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-bold mb-4">Rate This Course</h3>
          <div className="flex gap-2 mb-6">
            {[1, 2, 3, 4, 5].map((star) => (
              <button
                key={star}
                onClick={() => handleRatingClick(star)}
                onMouseEnter={() => setHoveredStar(star)}
                onMouseLeave={() => setHoveredStar(0)}
                className="text-3xl focus:outline-none transition-colors"
              >
                <span className={
                  star <= (hoveredStar || userRating) 
                    ? 'text-yellow-400' 
                    : 'text-gray-300'
                }>
                  ★
                </span>
              </button>
            ))}
            {userRating > 0 && (
              <span className="ml-2 text-gray-600 self-center">
                {userRating} star{userRating !== 1 ? 's' : ''}
              </span>
            )}
          </div>

          <h3 className="text-xl font-bold mb-4">Write a Review</h3>
          <form onSubmit={handleReviewSubmit}>
            <textarea
              value={newReview}
              onChange={(e) => setNewReview(e.target.value)}
              placeholder="Share your experience with this course..."
              rows={4}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <button
              type="submit"
              disabled={submitting || !newReview.trim()}
              className="mt-4 bg-blue-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {submitting ? 'Submitting...' : 'Submit Review'}
            </button>
          </form>
        </div>
      )}

      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-bold mb-6">
          Student Reviews ({reviews.length})
        </h3>
        
        {reviews.length > 0 ? (
          <div className="space-y-6">
            {reviews.map((review) => (
              <div key={review.id} className="border-b border-gray-200 pb-6 last:border-0">
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold">
                    {review.user_name?.[0]?.toUpperCase() || 'U'}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="font-semibold">{review.user_name || 'Anonymous'}</span>
                      <span className="text-gray-500 text-sm">
                        {new Date(review.created_at).toLocaleDateString()}
                      </span>
                    </div>
                    <p className="text-gray-700">{review.comment}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-center py-8">
            No reviews yet. {isEnrolled && 'Be the first to review this course!'}
          </p>
        )}
      </div>
    </div>
  );
}
