package de.chojo.callstats.configuration.file;

import de.chojo.callstats.configuration.file.elements.Data;
import de.chojo.callstats.configuration.file.elements.Security;
import de.chojo.callstats.configuration.file.elements.Web;

public class ConfigFile {
    private Data data = new Data();
    private Web web = new Web();
    private Security security = new Security();

    public ConfigFile() {
    }

    public Data data() {
        return data;
    }

    public Web web() {
        return web;
    }

    public Security security() {
        return security;
    }
}
