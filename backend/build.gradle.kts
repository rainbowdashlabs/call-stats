plugins {
    java
    application
}

group = "de.chojo"
version = "1.0.0"

repositories {
    mavenCentral()
    maven("https://eldonexus.de/repository/maven-public/")
}

java {
    toolchain {
        languageVersion = JavaLanguageVersion.of(21)
    }
}

application{
    mainClass = "de.chojo.callstats.Main"
}

dependencies {
    implementation(libs.bundles.sadu)
    implementation(libs.bundles.javalin)
    implementation(libs.postgres)
    implementation(libs.bundles.foundation)
    implementation("io.jsonwebtoken:jjwt-api:0.11.2")
    runtimeOnly("io.jsonwebtoken:jjwt-impl:0.11.2")
    runtimeOnly("io.jsonwebtoken:jjwt-jackson:0.11.2") // or 'io.jsonwebtoken:jjwt-gson:0.12.6' for gson

    annotationProcessor(libs.javalin.annotation)

    testImplementation(platform("org.junit:junit-bom:5.11.0"))
    testImplementation("org.junit.jupiter:junit-jupiter")
}

tasks {
    test {
        useJUnitPlatform()
    }
}
