export default function Footer() {
  return (
    <footer className="w-full bg-gray-50 border-t border-gray-200 py-6 mt-auto">
      <div className="max-w-7xl mx-auto px-4 text-center">
        <p className="text-sm text-gray-500">
          &copy; {new Date().getFullYear()} DevDeploy Inc. All rights reserved.
        </p>
      </div>
    </footer>
  );
}