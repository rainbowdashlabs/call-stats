package de.chojo.callstats.configuration;

import de.chojo.callstats.configuration.security.Auth;
import de.chojo.callstats.configuration.security.Role;
import de.chojo.callstats.controller.AuthController;
import de.chojo.callstats.controller.CallController;
import de.chojo.callstats.controller.CrewController;
import de.chojo.callstats.controller.ExerciseController;
import de.chojo.callstats.controller.RestController;
import de.chojo.callstats.controller.UserController;
import de.chojo.callstats.services.Services;
import io.javalin.Javalin;
import io.javalin.config.JavalinConfig;
import io.javalin.openapi.Security;
import io.javalin.openapi.plugin.OpenApiPlugin;
import io.javalin.openapi.plugin.swagger.SwaggerPlugin;

import java.util.List;

import static io.javalin.apibuilder.ApiBuilder.path;

public class WebConfiguration {
    private final Javalin javalin;
    private final Auth auth;
    private final List<RestController> controller;

    public WebConfiguration(FileConfiguration fileConfiguration, Services services) {
        this.auth = new Auth(services.jwtService());
        controller = List.of(
                new AuthController(services),
                new CallController(services.callService()),
                new CrewController(services.crewService()),
                new ExerciseController(services.exerciseService()),
                new UserController(services.userService()));
        this.javalin = Javalin.create(this::configure)
                              .start(fileConfiguration.web().host(), fileConfiguration.web().port());
    }

    public void configure(JavalinConfig config) {
        config.useVirtualThreads = true;
        config.staticFiles.add("frontend");
        config.registerPlugin(openApiPlugin());
        config.registerPlugin(swaggerPlugin());
        config.router.mount(router -> router.beforeMatched(auth::handleAccess));
        config.router.apiBuilder(this::routes);
    }

    private void routes() {
        path("/api/", () -> {
            controller.forEach(RestController::routes);
        });
    }

    private OpenApiPlugin openApiPlugin() {
        return new OpenApiPlugin(config -> {
            config.withRoles(Role.ANYONE);
            config.withDefinitionConfiguration((s, definitionConfiguration) -> {
                definitionConfiguration.withSecurity(security -> {
                    security.withBearerAuth();
                });
            });
        });
    }

    private SwaggerPlugin swaggerPlugin() {
        return new SwaggerPlugin(config -> {
            config.setUiPath("/docs");
            config.setRoles(new Role[]{Role.ANYONE});
        });
    }

    public Javalin javalin() {
        return javalin;
    }
}
