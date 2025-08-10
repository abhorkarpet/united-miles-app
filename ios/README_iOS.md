### United Miles iOS (SwiftUI)

This folder contains a native SwiftUI iOS app that mirrors the Streamlit app features:

- Ticket Purchase: Compare Miles, Cash, and Miles + Cash
- Upgrade Offer: Evaluate Miles+Cash vs Cash-only vs Full Fare with comfort factor and warnings
- Award Accelerator: Evaluate CPM and PQP value
- Buy Miles: Evaluate purchase value and CPM

#### Requirements
- Xcode 15+
- iOS 16+ target

#### Run
1. Create a new Xcode project named "UnitedMilesApp" (App, SwiftUI, iOS 16+) if a project file isn't already present.
2. Add the sources from `ios/UnitedMilesApp/` to the project (drag the `Models` and `Views` folders and `UnitedMilesAppApp.swift`).
3. Build & run on Simulator.

#### Structure
- `UnitedMilesAppApp.swift`: App entry point
- `Models/Valuations.swift`: Constants and enums
- `Models/Calculators.swift`: Core calculation logic ported from Streamlit
- `Views/TabRootView.swift`: Tab bar with 4 tabs
- `Views/*View.swift`: Feature-specific views

No external dependencies required.

Notes: United logo and external APIs are not included in iOS version by default. Add networking later if you integrate live data.


