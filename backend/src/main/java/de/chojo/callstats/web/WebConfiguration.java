package de.chojo.callstats.web;

import io.javalin.Javalin;
import io.javalin.config.JavalinConfig;

public class WebConfiguration {
    public WebConfiguration() {
        Javalin.create(this::configure);
    }

    public void configure(JavalinConfig config) {
        config.useVirtualThreads = true;
        config.staticFiles.add("frontend");
    }
}
