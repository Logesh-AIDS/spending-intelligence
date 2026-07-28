# Fix missing mipmap/ic_launcher resources

The build is failing because `AndroidManifest.xml` references `@mipmap/ic_launcher` and `@mipmap/ic_launcher_round`, but these resources are missing from the project. I will create a set of default adaptive icons to resolve this.

## Proposed Changes

### [:app](file:///Users/logeshalavandhan/Spending-Intelligence/android/app)

#### [NEW] [ic_launcher_background.xml](file:///Users/logeshalavandhan/Spending-Intelligence/android/app/src/main/res/drawable/ic_launcher_background.xml)
Create a background for the adaptive icon (solid color).

#### [NEW] [ic_launcher_foreground.xml](file:///Users/logeshalavandhan/Spending-Intelligence/android/app/src/main/res/drawable/ic_launcher_foreground.xml)
Create a foreground for the adaptive icon (simple vector).

#### [NEW] [ic_launcher.xml](file:///Users/logeshalavandhan/Spending-Intelligence/android/app/src/main/res/mipmap-anydpi-v26/ic_launcher.xml)
Define the adaptive icon using the background and foreground.

#### [NEW] [ic_launcher_round.xml](file:///Users/logeshalavandhan/Spending-Intelligence/android/app/src/main/res/mipmap-anydpi-v26/ic_launcher_round.xml)
Define the round adaptive icon.

## Verification Plan

### Automated Tests
- Run `./gradlew :app:processDebugResources` to verify that resource linking now succeeds.
