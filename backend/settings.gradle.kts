rootProject.name = "backend"

dependencyResolutionManagement {
    versionCatalogs {
        create("libs") {
            version("sadu", "2.3.0")
            library("sadu-postgresql", "de.chojo.sadu", "sadu-postgresql").versionRef("sadu")
            library("sadu-updater", "de.chojo.sadu", "sadu-updater").versionRef("sadu")
            library("sadu-queries", "de.chojo.sadu", "sadu-queries").versionRef("sadu")
            library("sadu-datasource", "de.chojo.sadu", "sadu-datasource").versionRef("sadu")
            bundle("sadu", listOf("sadu-postgresql", "sadu-updater", "sadu-queries", "sadu-datasource"))

            version("javalin", "6.3.0")
            library("javalin-bundle", "io.javalin", "javalin-bundle").versionRef("javalin")
            library("javalin-openapi", "io.javalin.community.openapi", "javalin-openapi-plugin").versionRef("javalin")
            library("javalin-swagger", "io.javalin.community.openapi", "javalin-swagger-plugin").versionRef("javalin")
            library("javalin-annotation", "io.javalin.community.openapi", "openapi-annotation-processor").versionRef("javalin")
            bundle("javalin", listOf("javalin-bundle", "javalin-openapi", "javalin-swagger"))

            version("foundation", "1.0.1")
            library("foundation-core", "dev.chojo.foundation", "core").versionRef("foundation")
            library("foundation-configuration", "dev.chojo.foundation", "configuration").versionRef("foundation")
            bundle("foundation", listOf("foundation-core", "foundation-configuration"))

            library("postgres","org.postgresql:postgresql:42.7.4")
        }
    }
}
