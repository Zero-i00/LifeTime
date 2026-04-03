
class PublicPage {
    readonly HOME = '/'

    private readonly AUTH = `${this.HOME}/auth`
    readonly LOGIN = `${this.AUTH}/login`
    readonly REGISTER = `${this.AUTH}/register`
}

class DashboardPage {
    readonly HOME = '/dashboard'

    readonly PROFILE = `${this.HOME}/profile`
}

export const PUBLIC_PAGE = new PublicPage()
export const DASHBOARD_PAGE = new DashboardPage()