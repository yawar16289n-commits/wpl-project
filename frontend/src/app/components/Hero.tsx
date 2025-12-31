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
          </div>
        </div>

   <div className="relative">
  <Image
    src="https://images.unsplash.com/photo-1457369804613-52c61a468e7d?q=80&w=1170&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
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
