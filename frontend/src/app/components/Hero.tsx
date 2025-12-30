import Image from 'next/image';
import Link from 'next/link';

export default function Hero() {
  return (
    <section className="w-full bg-gradient-to-r from-blue-50 to-indigo-50 py-24">
      <div className="max-w-7xl mx-auto px-6 grid md:grid-cols-2 gap-12 items-center">

        <div>
          <h2 className="text-5xl md:text-6xl font-bold leading-tight text-gray-900">
            Learn without limits
          </h2>
          <p className="mt-6 text-lg text-gray-600 leading-relaxed">
            Access world-class learning from universities and companies. Earn professional certificates and degrees online while working toward your personal and professional goals.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 mt-8">
            <Link href="/courses" className="bg-blue-600 text-white px-8 py-3 rounded font-medium hover:bg-blue-700 transition text-center">
              Explore Courses
            </Link>
            <button className="border-2 border-gray-300 text-gray-900 px-8 py-3 rounded font-medium hover:bg-gray-100 transition">
              Try for Free
            </button>
          </div>
        </div>

        <div className="relative">
          <Image 
            src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='600' height='400'%3E%3Crect fill='%23ddd' width='600' height='400'/%3E%3Ctext x='50%25' y='50%25' font-family='Arial' font-size='24' fill='%23999' text-anchor='middle' dominant-baseline='middle'%3ECourse Image%3C/text%3E%3C/svg%3E"
            alt="Learning"
            width={600}
            height={400}
            className="rounded-2xl shadow-2xl w-full h-auto"
          />
        </div>

      </div>
    </section>
  );
}
