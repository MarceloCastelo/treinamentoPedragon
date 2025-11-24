function createAdminNavbar() {
    return `
    <nav class="fixed top-0 left-0 right-0 z-50 bg-[#032B56] border-b border-yellow-600">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div class="flex justify-between items-center h-16">
                    <!-- Logo/Brand -->
                    <div class="flex-shrink-0">
                        <a href="/admin/dashboard" class="flex items-center">
                            <img src="/static/images/logos/ADTSA - BRANCA.png" alt="ADTSA" class="h-6 w-auto">
                            <span class="ml-3 text-yellow-300 text-sm font-semibold">ADMIN</span>
                        </a>
                    </div>
                    
                    <!-- Desktop Navigation -->
                    <div class="hidden md:block">
                        <div class="ml-10 flex items-baseline space-x-4">
                            <a href="/admin/dashboard" class="nav-link px-3 py-2 text-sm font-medium text-white hover:text-yellow-200 hover:bg-blue-700 rounded-md transition-colors duration-200">
                                <ion-icon name="analytics-outline" class="text-lg align-middle mr-1"></ion-icon>
                                Dashboard
                            </a>
                            <a href="/admin/reports" class="nav-link px-3 py-2 text-sm font-medium text-white hover:text-yellow-200 hover:bg-blue-700 rounded-md transition-colors duration-200">
                                <ion-icon name="document-text-outline" class="text-lg align-middle mr-1"></ion-icon>
                                Relatórios Detalhados
                            </a>
                            <a href="/auth/logout" class="nav-link px-3 py-2 text-sm font-medium text-white hover:text-blue-200 hover:bg-red-700 rounded-md transition-colors duration-200">
                                <ion-icon name="log-out-outline" class="text-lg align-middle mr-1"></ion-icon>
                                Sair
                            </a>
                        </div>
                    </div>

                    <!-- Mobile menu button -->
                    <div class="md:hidden">
                        <button id="navbar-hamburger" class="inline-flex items-center justify-center p-2 rounded-md text-white hover:text-yellow-200 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-yellow-500 transition-colors duration-200" aria-expanded="false">
                            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
                            </svg>
                        </button>
                    </div>
                </div>
            </div>

            <!-- Mobile menu -->
            <div id="navbar-mobile-menu" class="md:hidden hidden bg-[#032B56] border-b border-yellow-600">
                <div class="px-2 pt-2 pb-3 space-y-1">
                    <a href="/admin/dashboard" class="nav-link block px-3 py-2 text-base font-medium text-white hover:text-yellow-200 hover:bg-blue-700 rounded-md transition-colors duration-200">
                        <ion-icon name="analytics-outline" class="text-lg align-middle mr-1"></ion-icon>
                        Dashboard
                    </a>
                    <a href="/admin/reports" class="nav-link block px-3 py-2 text-base font-medium text-white hover:text-yellow-200 hover:bg-blue-700 rounded-md transition-colors duration-200">
                        <ion-icon name="document-text-outline" class="text-lg align-middle mr-1"></ion-icon>
                        Relatórios Detalhados
                    </a>
                    <a href="/auth/logout" class="nav-link block px-3 py-2 text-base font-medium text-white hover:text-blue-200 hover:bg-red-700 rounded-md transition-colors duration-200">
                        <ion-icon name="log-out-outline" class="text-lg align-middle mr-1"></ion-icon>
                        Sair
                    </a>
                </div>
            </div>
        </nav>
    `;
}

function createUserNavbar() {
    return `
    <nav class="fixed top-0 left-0 right-0 z-50 bg-[#032B56] border-b border-blue-800">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div class="flex justify-between items-center h-16">
                    <!-- Logo/Brand -->
                    <div class="flex-shrink-0">
                        <a href="/home" class="flex items-center">
                            <img src="/static/images/logos/ADTSA - BRANCA.png" alt="ADTSA" class="h-6 w-auto">
                        </a>
                    </div>
                    
                    <!-- Desktop Navigation -->
                    <div class="hidden md:block">
                        <div class="ml-10 flex items-baseline space-x-4">
                            <a href="/home" class="nav-link px-3 py-2 text-sm font-medium text-white hover:text-blue-200 hover:bg-blue-700 rounded-md transition-colors duration-200">
                                Home
                            </a>
                            
                            <!-- Dropdown Cursos -->
                            <div class="relative group">
                                <button class="nav-link px-3 py-2 text-sm font-medium text-white hover:text-blue-200 hover:bg-blue-700 rounded-md transition-colors duration-200 flex items-center">
                                    Cursos
                                    <ion-icon name="chevron-down-outline" class="ml-1 text-sm"></ion-icon>
                                </button>
                                <div class="absolute left-0 mt-2 w-48 bg-[#032B56] border border-blue-700 rounded-md shadow-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200">
                                    <a href="/my-courses" class="block px-4 py-3 text-sm text-white hover:bg-blue-700 hover:text-blue-200 transition-colors duration-200 rounded-t-md">
                                        <ion-icon name="book-outline" class="align-middle mr-2"></ion-icon>
                                        Meus Cursos
                                    </a>
                                    <a href="/all-courses" class="block px-4 py-3 text-sm text-white hover:bg-blue-700 hover:text-blue-200 transition-colors duration-200 rounded-b-md">
                                        <ion-icon name="library-outline" class="align-middle mr-2"></ion-icon>
                                        Todos os Cursos
                                    </a>
                                </div>
                            </div>
                            
                            <a href="/profile" class="nav-link px-3 py-2 text-sm font-medium text-white hover:text-blue-200 hover:bg-blue-700 rounded-md transition-colors duration-200">
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
                    <a href="/home" class="nav-link block px-3 py-2 text-base font-medium text-white hover:text-blue-200 hover:bg-blue-700 rounded-md transition-colors duration-200">
                        Home
                    </a>
                    
                    <!-- Submenu Cursos Mobile -->
                    <div class="pl-4 space-y-1">
                        <div class="text-xs font-semibold text-blue-300 uppercase tracking-wider px-3 py-2">
                            Cursos
                        </div>
                        <a href="/my-courses" class="nav-link block px-3 py-2 text-base font-medium text-white hover:text-blue-200 hover:bg-blue-700 rounded-md transition-colors duration-200">
                            <ion-icon name="book-outline" class="align-middle mr-2"></ion-icon>
                            Meus Cursos
                        </a>
                        <a href="/all-courses" class="nav-link block px-3 py-2 text-base font-medium text-white hover:text-blue-200 hover:bg-blue-700 rounded-md transition-colors duration-200">
                            <ion-icon name="library-outline" class="align-middle mr-2"></ion-icon>
                            Todos os Cursos
                        </a>
                    </div>
                    
                    <a href="/profile" class="nav-link block px-3 py-2 text-base font-medium text-white hover:text-blue-200 hover:bg-blue-700 rounded-md transition-colors duration-200">
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

function createNavbar() {
    // Verificar se usuário é admin
    const isAdmin = document.body.dataset.isAdmin === 'true';
    
    // Retornar navbar apropriada
    return isAdmin ? createAdminNavbar() : createUserNavbar();
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
