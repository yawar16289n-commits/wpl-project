export default function Footer() {
  return (
    <footer className="border-t border-gray-200 bg-white">
      <div className="max-w-7xl mx-auto px-6 py-16">

        <div className="flex flex-col md:flex-row justify-between items-center text-sm text-gray-600">
          <p>&copy; 2025 Coursera Inc. All rights reserved.</p>
          <div className="flex gap-6 mt-4 md:mt-0">
            <a href="#" className="hover:text-gray-900">Facebook</a>
            <a href="#" className="hover:text-gray-900">Twitter</a>
            <a href="#" className="hover:text-gray-900">LinkedIn</a>
            <a href="#" className="hover:text-gray-900">Instagram</a>
          </div>
        </div>

      </div>
    </footer>
  );
}
