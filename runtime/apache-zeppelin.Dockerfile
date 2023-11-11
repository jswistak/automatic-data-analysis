FROM apache/zeppelin:0.10.1

# Install Python 3.10 and all packages from default environment
RUN conda update conda && \
    conda config --add channels conda-forge && \
    conda config --set channel_priority strict

RUN conda list -n python_3_with_R --export > default_packages.txt && \
    sed -i 's/=.*//' default_packages.txt && \
    conda create -n python_3.10_with_R python=3.10 -y && \
    conda install -n python_3.10_with_R --file default_packages.txt

# Modify default Python interpreter path
RUN sed -i 's/python/\/opt\/conda\/envs\/python_3.10_with_R\/bin\/python/' /zeppelin/interpreter/python/