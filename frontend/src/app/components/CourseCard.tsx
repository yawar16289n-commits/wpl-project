import Link from 'next/link';
import Image from 'next/image';

const getValidImageUrl = (url: string | null | undefined): string => {
  if (!url) return '/placeholder.svg';
  
  try {
    const urlObj = new URL(url);
    const allowedHosts = ['images.unsplash.com', 'unsplash.com', 'picsum.photos'];
    
    if (allowedHosts.includes(urlObj.hostname)) {
      return url;
    }
  } catch (e) {
  }
  
  return '/placeholder.svg';
};

export default function CourseCard({
  title,
  image,
  id = '1',
  instructor,
  rating,
  students,
  level
}: {
  title: string;
  image: string;
  id?: string;
  instructor?: string;
  rating?: number;
  students?: number;
  level?: string;
}) {
  return (
    <Link href={`/course/${id}`}>
      <div className="bg-white rounded-lg shadow-md hover:shadow-xl transition-shadow duration-300 overflow-hidden cursor-pointer group">
        <div className="relative overflow-hidden bg-gray-200 h-48">
          <Image 
            src={getValidImageUrl(image)} 
            alt={title}
            width={400}
            height={192}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" 
          />
        </div>
        
        <div className="p-5">
          <h4 className="text-lg font-bold text-gray-900 mb-1">{title}</h4>
          {instructor && (
            <p className="text-gray-600 text-sm mb-2">{instructor}</p>
          )}
          
          {rating !== undefined && students !== undefined && (
            <div className="flex items-center gap-2 mb-3">
              <div className="flex items-center gap-1">
                <svg className="w-4 h-4 text-yellow-400 fill-current" viewBox="0 0 24 24">
                  <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                </svg>
                <span className="text-sm font-semibold text-gray-900">{rating}</span>
              </div>
              <span className="text-sm text-gray-600">({students?.toLocaleString()} students)</span>
            </div>
          )}

          <div className="flex items-center justify-between">
            {level && (
              <span className="text-xs font-medium text-gray-600 bg-gray-100 px-3 py-1 rounded-full">
                {level}
              </span>
            )}
          </div>
        </div>
      </div>
    </Link>
  );
}
