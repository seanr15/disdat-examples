import disdatluigi.api as api
from disdatluigi.pipe import PipeTask
from disdat.utility import aws_s3
from pyspark.sql import SparkSession
from pyspark import SparkConf
import luigi
import configparser
import os

data_context = 'example-context'

"""
        #self.create_remote_output_dir('job_output').replace('s3://', 's3a://', 1))
        # s3a_output_file.replace('s3a://', 's3://', 1)
"""


def get_spark_session(spark_master, app_name):
    aws_profile = "default"

    config = configparser.ConfigParser()
    config.read(os.path.expanduser("~/.aws/credentials"))
    access_id = config.get(aws_profile, "aws_access_key_id")
    access_key = config.get(aws_profile, "aws_secret_access_key")
    session_token = config.get(aws_profile, "aws_session_token")

    # https://github.com/aws/aws-sdk-java/issues/2510 -- use 3.2.2 
    os.environ['PYSPARK_SUBMIT_ARGS'] = "--packages=org.apache.hadoop:hadoop-aws:3.2.2 pyspark-shell"

    if spark_master is None:
        assert False, "Cannot get Spark session without a valid spark_master, bailing"

    conf = (
        SparkConf()
            .setAppName(app_name)
            .setMaster(spark_master)
            .set("fs.s3a.aws.credentials.provider","org.apache.hadoop.fs.s3a.TemporaryAWSCredentialsProvider")
            .set('spark.hadoop.fs.s3a.access.key', access_id)
            .set('spark.hadoop.fs.s3a.secret.key', access_key)
            .set('spark.hadoop.fs.s3a.session.token', session_token)
            #.set('spark.hadoop.fs.s3a.committer.name', 'directory')
            #.set('spark.sql.sources.commitProtocolClass', 'org.apache.spark.internal.io.cloud.PathOutputCommitProtocol')
            #.set('spark.sql.parquet.output.committer.class', 'org.apache.spark.internal.io.cloud.BindingParquetOutputCommitter')
    )
    return SparkSession.builder.config(conf=conf).getOrCreate()


def spark_line_count(spark, src_s3a_files, dst_dir):
    data = []
    for f in src_s3a_files:
        print("Spark reading file:{}".format(f))
        file_data = spark.read.text(f).cache()
        numAs = file_data.filter(file_data.value.contains('a')).count()
        numBs = file_data.filter(file_data.value.contains('b')).count()
        print("Lines with a: %i, lines with b: %i" % (numAs, numBs))
        data.append([numAs, numBs])
    df = spark.createDataFrame(data)
    df.write.format("parquet").save(dst_dir)
    files = aws_s3.ls_s3_url_keys(dst_dir.replace("s3a://","s3://",1))
    print(files)
    return files


class RunSparkJob(PipeTask):
    spark_master = luigi.Parameter(default=None)
    app_name = luigi.Parameter(default="DisdatSparkJob")
    input_bundle_name = luigi.Parameter(default='s3_files')

    def pipe_requires(self):
        self.set_bundle_name('DisdatSparkJob')
        self.add_external_dependency('s3_files',
                                     None,
                                     {},
                                     human_name=str(self.input_bundle_name))

    def pipe_run(self, s3_files):

        if not isinstance(s3_files, list):
            s3_files = [s3_files]

        s3a_files = [f.replace('s3://', 's3a://', 1) for f in s3_files]

        spark = get_spark_session(self.spark_master, self.app_name)

        output_dir = os.path.join(self.create_remote_output_dir('job_output')).replace('s3://', 's3a://', 1)

        output_files = spark_line_count(spark,
                                        s3a_files,
                                        output_dir)

        bucket, _ = aws_s3.split_s3_url(self.get_remote_output_dir())

        output_files = [os.path.join("s3://", os.path.join(bucket, f)) for f in output_files]

        spark.stop()

        return output_files


if __name__ == '__main__':
    api.apply(data_context,
              RunSparkJob)
