package technicalelvis.elephantBirdVectorConverter;

import java.io.IOException;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FileStatus;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.SequenceFile;
import org.apache.hadoop.io.Text;
import org.apache.log4j.Logger;
import org.apache.mahout.common.Pair;
import org.apache.mahout.common.iterator.sequencefile.PathType;
import org.apache.mahout.common.iterator.sequencefile.SequenceFileDirIterable;
import org.apache.mahout.math.NamedVector;
import org.apache.mahout.math.VectorWritable;

/**
 * Main() to convert Vectors in SequencFiles written by elephant-bird to
 * NamedVectors arg1 = input directory path arg2 = output directory path
 */
public class App {
    static Logger LOGGER = Logger.getLogger(App.class);
    static String usage = "Usage: hadoop jar JAR "
            + "technicalelvis.elephantBirdVectorConverter.App [inputdir] [outputdir]";

    public static void main(String[] args) {
        if (args.length != 2) {
            LOGGER.error(usage);
            System.exit(-1);
        }

        String in = args[0];
        String out = args[1];
        LOGGER.info(String.format("inputdir='%s', outputdir='%s'", in, out));
        try {
            // Open Input SequenceFile from Dir Path
            Configuration conf = new Configuration();
            FileSystem fs = FileSystem.get(conf);
            Path inputPath = new Path(in);
            FileStatus fstatus = fs.getFileStatus(inputPath);
            Path outputPath = new Path(out);
            // Check if input and output are dirs
            if (!fstatus.isDir()) {
                LOGGER.error(String.format("'%s' is not a directory.\n%s", in,
                        usage));
                System.exit(-1);
            }

            fstatus = fs.getFileStatus(outputPath);
            if (!fstatus.isDir()) {
                LOGGER.error(String.format("'%s' is not a directory.\n%s", out,
                        usage));
                System.exit(-1);
            }

            // Iterate over SequenceFile entries and output NamedVectors
            Text key = new Text();
            VectorWritable value = new VectorWritable();
            long id = 1;
            long cnt = 0;
            int fn_count = 0;
            Path outfile = new Path(outputPath, String.format("part-m-%05d",
                    fn_count++));
            SequenceFile.Writer writer = new SequenceFile.Writer(fs, conf,
                    outfile, Text.class, VectorWritable.class);
            for (Pair<Text, VectorWritable> entry : new SequenceFileDirIterable<Text, VectorWritable>(
                    new Path(inputPath, "part-*"), PathType.GLOB, conf)) {
                key = entry.getFirst();
                value = entry.getSecond();
                NamedVector vec = new NamedVector(value.get(), key.toString());
                value.set(vec);
                writer.append(new Text(Long.toString(id++)), value);
                cnt++;
                if (cnt >= 100000) {
                    LOGGER.info(String.format(
                            "Wrote '%d' namedvectors to '%s'", cnt,
                            outfile.toString()));
                    writer.close();
                    cnt = 0;
                    outfile = new Path(outputPath, String.format("part-m-%05d",
                            fn_count++));
                }
            }
            // write remaining entries
            if (cnt > 0) {
                writer.close();
                LOGGER.info(String.format("Wrote '%d' namedvectors to '%s'",
                        cnt, outfile.toString()));
            }
        } catch (IOException e) {
            LOGGER.error(e.getMessage(), e);
        }
    }
}
