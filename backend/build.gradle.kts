plugins {
    java
}

group = "de.chojo"
version = "1.0.0"

repositories {
    mavenCentral()
}

java {
    toolchain {
        languageVersion = JavaLanguageVersion.of(21)
    }
}

dependencies {
    implementation(libs.bundles.sadu)
    implementation(libs.bundles.javalin)
    implementation(libs.postgres)
    annotationProcessor(libs.javalin.openapiannotation)
    testImplementation(platform("org.junit:junit-bom:5.11.0"))
    testImplementation("org.junit.jupiter:junit-jupiter")
}

tasks {
    test {
        useJUnitPlatform()
    }
}
