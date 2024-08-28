package de.chojo.callstats.services;

import com.fasterxml.jackson.annotation.JsonAutoDetect;
import com.fasterxml.jackson.annotation.PropertyAccessor;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.databind.MapperFeature;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.json.JsonMapper;
import de.chojo.callstats.configuration.FileConfiguration;
import de.chojo.callstats.configuration.file.elements.Security;
import de.chojo.callstats.entites.User;
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;
import io.jsonwebtoken.security.Keys;

import java.security.Key;
import java.util.Collections;
import java.util.Date;
import java.util.Map;
import java.util.concurrent.ThreadLocalRandom;
import java.util.function.Function;

public class JwtService {
    public static final Map<String, Object> LOGIN_CLAIM = Map.of("type", "login");
    public static final Map<String, Object> REFRESH_CLAIM = Map.of("type", "refresh");

    private final FileConfiguration fileConfiguration;
    private final ObjectMapper objectMapper;

    public JwtService(FileConfiguration fileConfiguration) {
        this.fileConfiguration = fileConfiguration;
        objectMapper = JsonMapper.builder().configure(MapperFeature.ALLOW_FINAL_FIELDS_AS_MUTATORS, true).build()
                                 .configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false)
                                 .setVisibility(PropertyAccessor.FIELD, JsonAutoDetect.Visibility.ANY)
                                 .setVisibility(PropertyAccessor.GETTER, JsonAutoDetect.Visibility.NONE);
    }

    public User extractUser(String token) {
        return extractClaim(token, c -> {
            try {
                return objectMapper.readValue(c.getSubject(), User.class);
            } catch (JsonProcessingException e) {
                throw new RuntimeException(e);
            }
        });
    }

    public <T> T extractClaim(String token, Function<Claims, T> claimsResolver) {
        final Claims claims = extractAllClaims(token);
        return claimsResolver.apply(claims);
    }

    public String generateToken(User userDetails) {
        return generateToken(Collections.emptyMap(), userDetails);
    }

    public String generateToken(Map<String, Object> extraClaims, User userDetails) {
        return generateToken(extraClaims, userDetails, fileConfiguration.security().jwtExpiration());
    }

    public String generateToken(
            Map<String, Object> extraClaims,
            User userDetails,
            long expiration
    ) {
        return Jwts
                .builder()
                .setClaims(extraClaims)
                .claim("nonce", ThreadLocalRandom.current().nextLong(1000000000))
                .setSubject(userDetails.name())
                .setIssuedAt(new Date(System.currentTimeMillis()))
                .setExpiration(new Date(System.currentTimeMillis() + expiration))
                .signWith(getSignInKey(), SignatureAlgorithm.HS256)
                .compact();
    }

    public boolean isTokenValid(String token, User userDetails, Map<String, Object> claims) {
        if (!userDetails.equals(extractUser(token))) return false;
        if (isTokenExpired(token)) return false;
        Claims allClaims = extractAllClaims(token);
        for (var entry : claims.entrySet()) {
            if (!allClaims.get(entry.getKey()).equals(entry.getValue())) return false;
        }
        return true;
    }

    private boolean isTokenExpired(String token) {
        return extractExpiration(token).before(new Date());
    }

    private Date extractExpiration(String token) {
        return extractClaim(token, Claims::getExpiration);
    }

    private Claims extractAllClaims(String token) {
        return Jwts
                .parserBuilder()
                .setSigningKey(getSignInKey())
                .build()
                .parseClaimsJws(token)
                .getBody();
    }

    private Key getSignInKey() {
        return Keys.hmacShaKeyFor(fileConfiguration.security().secretKey().getBytes());
    }

    public long jwtExpiration() {
        return fileConfiguration.security().jwtExpiration();
    }

    public long jwtRefreshExpiration() {
        return fileConfiguration.security().jwtRefreshExpiration();
    }
}
