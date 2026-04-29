function createAdminNavbar() {
    return `
    <nav class="fixed top-0 left-0 right-0 z-50 bg-black border-b border-gray-800 shadow-sm">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between items-center h-16">
                <div class="flex-shrink-0">
                    <a href="/admin/dashboard" class="flex items-center">
                        <img src="/static/images/logos/pedragon2_branca.png" alt="Pedragon" class="h-16 w-auto">
                        <span class="ml-3 text-blue-400 text-sm font-semibold">ADMIN</span>
                    </a>
                </div>
                <div class="hidden md:block">
                    <div class="ml-10 flex items-baseline space-x-4">
                        <a href="/admin/dashboard" class="nav-link px-3 py-2 text-sm font-medium text-white hover:text-blue-400 hover:bg-gray-800 rounded-md transition-colors duration-200">
                            <ion-icon name="analytics-outline" class="text-lg align-middle mr-1"></ion-icon>
                            Dashboard
                        </a>
                        <a href="/admin/reports" class="nav-link px-3 py-2 text-sm font-medium text-white hover:text-blue-400 hover:bg-gray-800 rounded-md transition-colors duration-200">
                            <ion-icon name="document-text-outline" class="text-lg align-middle mr-1"></ion-icon>
                            Relatórios Detalhados
                        </a>
                        <a href="/auth/logout" class="nav-link px-3 py-2 text-sm font-medium text-white hover:text-red-400 hover:bg-gray-800 rounded-md transition-colors duration-200">
                            <ion-icon name="log-out-outline" class="text-lg align-middle mr-1"></ion-icon>
                            Sair
                        </a>
                    </div>
                </div>
                <div class="md:hidden">
                    <button id="navbar-hamburger" class="inline-flex items-center justify-center p-2 rounded-md text-white hover:text-blue-400 hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500 transition-colors duration-200">
                        <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
                        </svg>
                    </button>
                </div>
            </div>
        </div>
        <div id="navbar-mobile-menu" class="md:hidden hidden bg-black border-b border-gray-800">
            <div class="px-2 pt-2 pb-3 space-y-1">
                <a href="/admin/dashboard" class="nav-link block px-3 py-2 text-base font-medium text-white hover:text-blue-400 hover:bg-gray-800 rounded-md transition-colors duration-200">
                    Dashboard
                </a>
                <a href="/admin/reports" class="nav-link block px-3 py-2 text-base font-medium text-white hover:text-blue-400 hover:bg-gray-800 rounded-md transition-colors duration-200">
                    Relatórios Detalhados
                </a>
                <a href="/auth/logout" class="nav-link block px-3 py-2 text-base font-medium text-white hover:text-red-400 hover:bg-gray-800 rounded-md transition-colors duration-200">
                    Sair
                </a>
            </div>
        </div>
    </nav>
    `;
}

function createUserNavbar() {
    return `
    <nav class="fixed top-0 left-0 right-0 z-50 bg-black border-b border-gray-800 shadow-sm">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between items-center h-16">
                <div class="flex-shrink-0">
                    <a href="/home" class="flex items-center">
                        <img src="/static/images/logos/pedragon2_branca.png" alt="Pedragon" class="h-16 w-auto">
                    </a>
                </div>
                <div class="hidden md:block">
                    <div class="ml-10 flex items-baseline space-x-4">
                        <a href="/home" class="nav-link px-3 py-2 text-sm font-medium text-white hover:text-blue-400 hover:bg-gray-800 rounded-md transition-colors duration-200">
                            Home
                        </a>
                        <div class="relative group">
                            <button class="nav-link px-3 py-2 text-sm font-medium text-white hover:text-blue-400 hover:bg-gray-800 rounded-md transition-colors duration-200 flex items-center">
                                Cursos
                                <ion-icon name="chevron-down-outline" class="ml-1 text-sm"></ion-icon>
                            </button>
                            <div class="absolute left-0 mt-2 w-48 bg-black border border-gray-700 rounded-md shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200">
                                <a href="/my-courses" class="block px-4 py-3 text-sm text-white hover:bg-gray-800 hover:text-blue-400 transition-colors duration-200 rounded-t-md">
                                    <ion-icon name="book-outline" class="align-middle mr-2"></ion-icon>
                                    Meus Cursos
                                </a>
                                <a href="/all-courses" class="block px-4 py-3 text-sm text-white hover:bg-gray-800 hover:text-blue-400 transition-colors duration-200 rounded-b-md">
                                    <ion-icon name="library-outline" class="align-middle mr-2"></ion-icon>
                                    Todos os Cursos
                                </a>
                            </div>
                        </div>
                        <a href="/profile" class="nav-link px-3 py-2 text-sm font-medium text-white hover:text-blue-400 hover:bg-gray-800 rounded-md transition-colors duration-200">
                            Meu Perfil
                        </a>
                        <a href="/auth/logout" class="nav-link px-3 py-2 text-sm font-medium text-white hover:text-red-400 hover:bg-gray-800 rounded-md transition-colors duration-200">
                            Sair
                        </a>
                    </div>
                </div>
                <div class="md:hidden">
                    <button id="navbar-hamburger" class="inline-flex items-center justify-center p-2 rounded-md text-white hover:text-blue-400 hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500 transition-colors duration-200">
                        <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
                        </svg>
                    </button>
                </div>
            </div>
        </div>
        <div id="navbar-mobile-menu" class="md:hidden hidden bg-black border-b border-gray-800">
            <div class="px-2 pt-2 pb-3 space-y-1">
                <a href="/home" class="nav-link block px-3 py-2 text-base font-medium text-white hover:text-blue-400 hover:bg-gray-800 rounded-md transition-colors duration-200">
                    Home
                </a>
                <div class="pl-4 space-y-1">
                    <div class="text-xs font-semibold text-gray-500 uppercase tracking-wider px-3 py-2">Cursos</div>
                    <a href="/my-courses" class="nav-link block px-3 py-2 text-base font-medium text-white hover:text-blue-400 hover:bg-gray-800 rounded-md transition-colors duration-200">
                        Meus Cursos
                    </a>
                    <a href="/all-courses" class="nav-link block px-3 py-2 text-base font-medium text-white hover:text-blue-400 hover:bg-gray-800 rounded-md transition-colors duration-200">
                        Todos os Cursos
                    </a>
                </div>
                <a href="/profile" class="nav-link block px-3 py-2 text-base font-medium text-white hover:text-blue-400 hover:bg-gray-800 rounded-md transition-colors duration-200">
                    Meu Perfil
                </a>
                <a href="/auth/logout" class="nav-link block px-3 py-2 text-base font-medium text-white hover:text-red-400 hover:bg-gray-800 rounded-md transition-colors duration-200">
                    Sair
                </a>
            </div>
        </div>
    </nav>
    `;
}

function createNavbar() {
    const isAdmin = document.body.dataset.isAdmin === 'true';
    return isAdmin ? createAdminNavbar() : createUserNavbar();
}

function initNavbar() {
    const container = document.getElementById('navbar-container');
    if (container) {
        container.innerHTML = createNavbar();

        // Hamburger menu toggle
        const hamburger = document.getElementById('navbar-hamburger');
        const mobileMenu = document.getElementById('navbar-mobile-menu');

        if (hamburger && mobileMenu) {
            hamburger.addEventListener('click', function() {
                const isOpen = !mobileMenu.classList.contains('hidden');
                if (isOpen) {
                    mobileMenu.classList.add('hidden');
                    hamburger.setAttribute('aria-expanded', 'false');
                } else {
                    mobileMenu.classList.remove('hidden');
                    hamburger.setAttribute('aria-expanded', 'true');
                }
            });
        }

        highlightCurrentPage();
    }
}

function highlightCurrentPage() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');

    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('bg-gray-800', 'text-blue-400');
        }
    });
}

document.addEventListener('DOMContentLoaded', initNavbar);
