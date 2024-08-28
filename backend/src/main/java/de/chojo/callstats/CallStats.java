package de.chojo.callstats;

import de.chojo.callstats.configuration.DataConfiguration;
import de.chojo.callstats.configuration.FileConfiguration;
import de.chojo.callstats.configuration.WebConfiguration;
import de.chojo.callstats.services.Services;

import java.io.IOException;
import java.sql.SQLException;

public class CallStats {
    private static CallStats instance;

    public static void main(String[] args) throws SQLException, IOException {
        instance = new CallStats();
        instance.init();
    }

    private void init() throws SQLException, IOException {
        FileConfiguration fileConfiguration = new FileConfiguration();
        DataConfiguration dataConfiguration = new DataConfiguration(fileConfiguration);
        Services services = new Services(dataConfiguration.repositories(), fileConfiguration);
        WebConfiguration webConfiguration = new WebConfiguration(fileConfiguration, services);
    }
}
