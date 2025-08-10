import SwiftUI

struct TabRootView: View {
    var body: some View {
        TabView {
            TicketPurchaseView()
                .tabItem { Label("Ticket", systemImage: "ticket") }
            UpgradeOfferView()
                .tabItem { Label("Upgrade", systemImage: "arrow.up.circle") }
            AwardAcceleratorView()
                .tabItem { Label("Accelerator", systemImage: "bolt") }
            BuyMilesView()
                .tabItem { Label("Buy Miles", systemImage: "cart") }
        }
    }
}

struct TabRootView_Previews: PreviewProvider {
    static var previews: some View {
        TabRootView()
    }
}


