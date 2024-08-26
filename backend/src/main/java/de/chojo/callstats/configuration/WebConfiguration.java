package de.chojo.callstats.configuration;

import io.javalin.Javalin;
import io.javalin.config.JavalinConfig;

public class WebConfiguration {
    private final Javalin javalin;

    public WebConfiguration() {
        this.javalin = Javalin.create(this::configure);
    }

    public void configure(JavalinConfig config) {
        config.useVirtualThreads = true;
        config.staticFiles.add("frontend");
    }

    public Javalin javalin() {
        return javalin;
    }
}
