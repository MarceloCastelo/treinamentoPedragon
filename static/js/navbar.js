function createNavbar() {
    return `
    <nav class="fixed top-0 left-0 right-0 z-50 bg-[#032B56] border-b border-blue-800">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div class="flex justify-between items-center h-16">
                    <!-- Logo/Brand -->
                    <div class="flex-shrink-0">
                        <a href="/" class="flex items-center">
                            <img src="/static/images/logos/ADTSA - BRANCA.png" alt="ADTSA" class="h-6 w-auto">
                        </a>
                    </div>
                    
                    <!-- Desktop Navigation -->
                    <div class="hidden md:block">
                        <div class="ml-10 flex items-baseline space-x-4">
                            <a href="/" class="nav-link px-3 py-2 text-sm font-medium text-white hover:text-blue-200 hover:bg-blue-700 rounded-md transition-colors duration-200">
                                Home
                            </a>
                            <a href="/auth/my-courses" class="nav-link px-3 py-2 text-sm font-medium text-white hover:text-blue-200 hover:bg-blue-700 rounded-md transition-colors duration-200">
                                Meus Cursos
                            </a>
                            <a href="/auth/profile" class="nav-link px-3 py-2 text-sm font-medium text-white hover:text-blue-200 hover:bg-blue-700 rounded-md transition-colors duration-200">
                                Meu Perfil
                            </a>
                            <a href="/auth/logout" class="nav-link px-3 py-2 text-sm font-medium text-white hover:text-blue-200 hover:bg-red-700 rounded-md transition-colors duration-200">
                                Sair
                            </a>
                        </div>
                    </div>

                    <!-- Mobile menu button -->
                    <div class="md:hidden">
                        <button id="navbar-hamburger" class="inline-flex items-center justify-center p-2 rounded-md text-white hover:text-blue-200 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500 transition-colors duration-200" aria-expanded="false">
                            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
                            </svg>
                        </button>
                    </div>
                </div>
            </div>

            <!-- Mobile menu -->
            <div id="navbar-mobile-menu" class="md:hidden hidden bg-[#032B56] border-b border-blue-800">
                <div class="px-2 pt-2 pb-3 space-y-1">
                    <a href="/" class="nav-link block px-3 py-2 text-base font-medium text-white hover:text-blue-200 hover:bg-blue-700 rounded-md transition-colors duration-200">
                        Home
                    </a>
                    <a href="/auth/my-courses" class="nav-link block px-3 py-2 text-base font-medium text-white hover:text-blue-200 hover:bg-blue-700 rounded-md transition-colors duration-200">
                        Meus Cursos
                    </a>
                    <a href="/auth/profile" class="nav-link block px-3 py-2 text-base font-medium text-white hover:text-blue-200 hover:bg-blue-700 rounded-md transition-colors duration-200">
                        Meu Perfil
                    </a>
                    <a href="/auth/logout" class="nav-link block px-3 py-2 text-base font-medium text-white hover:text-blue-200 hover:bg-red-700 rounded-md transition-colors duration-200">
                        Sair
                    </a>
                </div>
            </div>
        </nav>
    `;
}

function initNavbar() {
    // Inserir a navbar no elemento com id 'navbar-container'
    const navbarContainer = document.getElementById('navbar-container');
    if (navbarContainer) {
        navbarContainer.innerHTML = createNavbar();

        // Destacar página atual
        highlightCurrentPage();

        // Mobile menu logic
        const hamburger = document.getElementById('navbar-hamburger');
        const mobileMenu = document.getElementById('navbar-mobile-menu');

        if (hamburger && mobileMenu) {
            hamburger.addEventListener('click', () => {
                mobileMenu.classList.toggle('hidden');
            });

            // Fechar menu ao clicar em um link
            const mobileLinks = mobileMenu.querySelectorAll('a');
            mobileLinks.forEach(link => {
                link.addEventListener('click', () => {
                    mobileMenu.classList.add('hidden');
                });
            });

            // Fechar menu ao clicar fora (opcional)
            document.addEventListener('click', (e) => {
                if (!hamburger.contains(e.target) && !mobileMenu.contains(e.target)) {
                    mobileMenu.classList.add('hidden');
                }
            });
        }
    }
}

function highlightCurrentPage() {
    const currentPage = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');

    navLinks.forEach(link => {
        const href = link.getAttribute('href') || '';
        
        // Remove destaque anterior
        link.classList.remove('bg-blue-800', 'text-blue-100');
        
        // Adiciona destaque apenas na opção selecionada
        if (href === currentPage || (href === '/' && currentPage === '/')) {
            link.classList.add('bg-blue-800', 'text-blue-100');
            link.classList.remove('text-white', 'hover:text-blue-200', 'hover:bg-blue-700');
        }
    });
}

// Inicializar quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', initNavbar);
