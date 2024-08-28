package de.chojo.callstats.configuration;

import de.chojo.callstats.configuration.file.ConfigFile;
import de.chojo.callstats.configuration.file.elements.Data;
import de.chojo.callstats.configuration.file.elements.Security;
import de.chojo.callstats.configuration.file.elements.Web;
import dev.chojo.foundation.configuration.BaseConfiguration;

public class FileConfiguration extends BaseConfiguration<ConfigFile> {
    public FileConfiguration() {
        super(new ConfigFile());
        reload();
    }

    public Data data() {
        return config.data();
    }

    public Web web() {
        return config.web();
    }

    public Security security() {
        return config.security();
    }
}
