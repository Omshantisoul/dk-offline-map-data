import btools.router.OsmNodeNamed;
import btools.router.RoutingContext;
import btools.router.RoutingEngine;
import java.io.File;
import java.util.ArrayList;

/** Offline, in-process BRouter smoke probe used only by the Phase 9 workflow. */
public final class BRouterCliProbe {
  public static void main(String[] args) throws Exception {
    if (args.length != 6) throw new IllegalArgumentException("profile segmentDir lat1 lon1 lat2 lon2");
    String profile = args[0];
    File segments = new File(args[1]);
    double lat1 = Double.parseDouble(args[2]), lon1 = Double.parseDouble(args[3]);
    double lat2 = Double.parseDouble(args[4]), lon2 = Double.parseDouble(args[5]);
    RoutingContext rc = new RoutingContext();
    rc.localFunction = profile;
    rc.memoryclass = 256;
    btools.router.ProfileCache.setSize(2);
    btools.router.ProfileCache.parseProfile(rc);
    rc.initModel();
    ArrayList<OsmNodeNamed> waypoints = new ArrayList<>();
    waypoints.add(point(lat1, lon1, "start"));
    waypoints.add(point(lat2, lon2, "end"));
    long start = System.nanoTime();
    RoutingEngine engine = new RoutingEngine(null, null, segments, waypoints, rc);
    engine.start(); engine.join();
    long elapsed = (System.nanoTime() - start) / 1_000_000;
    System.out.println("elapsedMs=" + elapsed + ",finished=" + engine.isFinished()
        + ",error=" + engine.getErrorMessage() + ",distanceM=" + engine.getDistance()
        + ",track=" + (engine.getFoundTrack() != null));
  }
  private static OsmNodeNamed point(double lat, double lon, String name) {
    OsmNodeNamed p = new OsmNodeNamed();
    p.ilat = (int) Math.round((lat + 90d) * 1_000_000d);
    p.ilon = (int) Math.round((lon + 180d) * 1_000_000d);
    p.name = name; return p;
  }
}
